#!/usr/bin/env python3
"""
RDS Database Connection Manager

A Python utility for connecting to AWS RDS databases with IAM-based authentication,
connection logging, and database catalog management.

This tool simplifies database connections by handling token generation, user resolution,
and connection logging automatically.
"""

import os
import sys
import json
import subprocess
import argparse
import time
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


@dataclass
class DatabaseConfig:
    """Database configuration from catalog"""

    alias: str
    dbname: str
    db_endpoint: str
    port: int
    region: str
    account_id: str
    env: str


class RDSConnectionManager:
    """Manages AWS RDS connections with IAM authentication"""

    DEFAULT_PORT = 5432
    DEFAULT_REGION = "ap-south-1"
    DEFAULT_DB_USER = "appuser"
    CATALOG_SCHEMA = [
        "alias",
        "dbname",
        "db_endpoint",
        "port",
        "region",
        "account_id",
        "env",
    ]

    def __init__(self, catalog_path: str, log_path: Optional[str] = None):
        """
        Initialize the connection manager.

        Args:
            catalog_path: Path to database catalog JSON file
            log_path: Optional path for connection logs
        """
        self.catalog_path = Path(catalog_path)
        self.log_path = Path(log_path) if log_path else None
        self.logger = self._setup_logger()
        self.psql_bin = shutil.which("psql") or "psql"
        self.aws_cli = shutil.which("aws") or "aws"
        self.catalog = self._load_catalog()

    def _setup_logger(self) -> logging.Logger:
        """Configure logging"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _load_catalog(self) -> List[Dict[str, Any]]:
        """Load and validate database catalog."""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found at {self.catalog_path}")

        try:
            with open(self.catalog_path, "r") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("Catalog must be a JSON list of database configs")

                for entry in data:
                    self._validate_catalog_entry(entry)

                return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in catalog: {e}")

    def _validate_catalog_entry(self, entry: Dict[str, Any]) -> None:
        """Validate a single database catalog entry."""
        if not isinstance(entry, dict):
            raise ValueError("Each catalog entry must be a JSON object")

        for field in self.CATALOG_SCHEMA:
            if field not in entry:
                raise ValueError(f"Catalog entry is missing required field: {field}")

        if not isinstance(entry["port"], int):
            raise ValueError("Catalog entry port must be an integer")

    def _write_log(self, log_entry: Dict[str, Any]) -> None:
        """Write connection event to log file"""
        if not self.log_path:
            return

        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            self.logger.warning(f"Failed to write log: {e}")

    def get_caller_identity(self) -> str:
        """Get AWS caller identity ARN"""
        try:
            if BOTO3_AVAILABLE:
                sts = boto3.client("sts")
                response = sts.get_caller_identity()
                return response.get("Arn", "unknown")
            else:
                output = subprocess.check_output(
                    [
                        self.aws_cli,
                        "sts",
                        "get-caller-identity",
                        "--query",
                        "Arn",
                        "--output",
                        "text",
                    ],
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                return output.strip()
        except Exception:
            return "unknown"

    def resolve_db_username(self, explicit_user: Optional[str] = None) -> str:
        """
        Resolve database username from various sources.

        Priority:
        1. Explicit user argument
        2. Linux environment variables (USER, LOGNAME)
        3. AWS IAM identity
        4. Default user
        """
        if explicit_user:
            return explicit_user

        linux_user = os.getenv("USER") or os.getenv("LOGNAME")
        if linux_user:
            if "@" in linux_user:
                linux_user = linux_user.split("@")[0]
            return linux_user

        try:
            arn = self.get_caller_identity()
            if arn and "/" in arn:
                session = arn.split("/")[-1]
                if session:
                    return session
        except Exception:
            pass

        return self.DEFAULT_DB_USER

    def generate_auth_token(
        self, host: str, port: int, region: str, username: str
    ) -> str:
        """Generate temporary RDS authentication token."""
        if BOTO3_AVAILABLE:
            try:
                client = boto3.client("rds", region_name=region)
                try:
                    token = client.generate_db_auth_token(
                        DBHostname=host, Port=port, DBUsername=username
                    )
                except TypeError:
                    token = client.generate_db_auth_token(
                        Hostname=host, Port=port, Username=username
                    )
                return token
            except (BotoCoreError, ClientError) as e:
                self.logger.debug(f"Boto3 token generation failed: {e}")

        try:
            output = subprocess.check_output(
                [
                    self.aws_cli,
                    "rds",
                    "generate-db-auth-token",
                    "--hostname",
                    host,
                    "--port",
                    str(port),
                    "--region",
                    region,
                    "--username",
                    username,
                ],
                stderr=subprocess.STDOUT,
                text=True,
            )
            return output.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Token generation failed: {e.output}")

    def find_databases(
        self, search_term: Optional[str] = None, exact: bool = False
    ) -> List[DatabaseConfig]:
        """Search for databases in catalog."""
        if not search_term:
            return [self._to_config(db) for db in self.catalog]

        matches = []
        for db in self.catalog:
            alias = db.get("alias", "")
            dbname = db.get("dbname", "")

            if exact:
                if alias == search_term:
                    matches.append(self._to_config(db))
            else:
                search_lower = search_term.lower()
                if alias.lower() == search_lower or dbname.lower() == search_lower:
                    matches.append(self._to_config(db))

        return matches

    def find_suggestions(
        self, search_term: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get fuzzy suggestions for partial matches"""
        suggestions = []
        search_lower = search_term.lower()

        for db in self.catalog:
            combined = (db.get("dbname", "") + " " + db.get("alias", "")).lower()
            if search_lower in combined:
                suggestions.append(
                    {
                        "alias": db.get("alias"),
                        "dbname": db.get("dbname"),
                        "account_id": db.get("account_id"),
                        "env": db.get("env"),
                    }
                )

        return suggestions[:limit]

    def list_databases(self) -> None:
        """Display all available databases in table format"""
        if not self.catalog:
            print("No databases in catalog")
            return

        print("\nAvailable Databases:")
        print("-" * 80)
        print(
            f"{'Alias':<20} {'Database':<20} {'Account':<15} {'Env':<8} {'Endpoint':<15}"
        )
        print("-" * 80)

        for db in self.catalog:
            env = db.get("env", "").upper()
            prod_marker = " [PROD]" if env == "PROD" else ""
            print(
                f"{db.get('alias', '-'):<20} "
                f"{db.get('dbname', '-'):<20} "
                f"{db.get('account_id', '-'):<15} "
                f"{env:<8} "
                f"{db.get('db_endpoint', '-'):<15}{prod_marker}"
            )
        print("-" * 80)

    def connect(
        self, config: DatabaseConfig, username: str, preview_only: bool = False
    ) -> None:
        """Establish database connection."""
        log_entry: Dict[str, Any] = {
            "event": "connect_attempt",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "alias": config.alias,
            "dbname": config.dbname,
            "account": config.account_id,
            "env": config.env,
            "dbuser": username,
            "caller_arn": self.get_caller_identity(),
            "os_user": os.getenv("USER") or os.getenv("LOGNAME") or "unknown",
        }

        print(
            f"\n[Connecting] alias={config.alias} db={config.dbname} "
            f"account={config.account_id} env={config.env} user={username}"
        )

        if preview_only:
            print(f"\n[Preview Mode]")
            print(f"Endpoint: {config.db_endpoint}:{config.port}")
            print(f"Database: {config.dbname}")
            print(f"Username: {username}")
            print(f"Region: {config.region}\n")
            return

        start_time = time.time()

        try:
            token = self.generate_auth_token(
                config.db_endpoint,
                config.port,
                config.region,
                username,
            )

            token_time = time.time() - start_time
            log_entry.update(
                {
                    "event": "token_generated",
                    "token_ms": int(token_time * 1000),
                }
            )

            env = os.environ.copy()
            env["PGPASSWORD"] = token
            psql_args = [
                self.psql_bin,
                f"host={config.db_endpoint}",
                f"port={config.port}",
                f"user={username}",
                f"dbname={config.dbname}",
                "sslmode=require",
            ]

            self._write_log(log_entry)
            os.execvpe(self.psql_bin, psql_args, env)

        except Exception as e:
            log_entry.update({"result": "error", "error": str(e)})
            self._write_log(log_entry)
            raise

    @staticmethod
    def _to_config(db_dict: Dict[str, Any]) -> DatabaseConfig:
        """Convert database dict to DatabaseConfig object"""
        return DatabaseConfig(
            alias=db_dict.get("alias", ""),
            dbname=db_dict.get("dbname", ""),
            db_endpoint=db_dict.get("db_endpoint", ""),
            port=int(db_dict.get("port", 5432)),
            region=db_dict.get("region", "ap-south-1"),
            account_id=db_dict.get("account_id", ""),
            env=db_dict.get("env", ""),
        )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="RDS Database Connection Manager - Connect to AWS RDS with IAM authentication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available databases
  %(prog)s --list
  
  # Connect to database by name or alias
  %(prog)s mydb
  
  # Preview connection without connecting
  %(prog)s mydb --preview
  
  # Connect as specific user
  %(prog)s mydb --user dbadmin
  
  # Non-interactive mode (fail if multiple matches)
  %(prog)s mydb --no-prompt
        """,
    )

    parser.add_argument(
        "database", nargs="?", help="Database name or alias to connect to"
    )
    parser.add_argument("--alias", help="Connect using exact alias match")
    parser.add_argument("--user", help="Override database username")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview connection details without connecting",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Non-interactive mode (fail if multiple matches)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List all available databases"
    )
    parser.add_argument(
        "--catalog",
        default=os.environ.get("RDS_CATALOG", "db_catalog.json"),
        help="Path to database catalog (default: db_catalog.json)",
    )
    parser.add_argument(
        "--log",
        default=os.environ.get("RDS_LOG", None),
        help="Path to connection log file",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    try:
        manager = RDSConnectionManager(args.catalog, args.log)

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        if args.list:
            manager.list_databases()
            return

        search_term = args.alias or args.database
        if not search_term:
            try:
                search_term = input(
                    "Enter database name or alias (or 'list' to see all): "
                ).strip()
                if search_term.lower() == "list":
                    manager.list_databases()
                    return
                if not search_term:
                    print("No database provided", file=sys.stderr)
                    sys.exit(3)
            except KeyboardInterrupt:
                print("\nCancelled", file=sys.stderr)
                sys.exit(4)

        matches = manager.find_databases(search_term, exact=bool(args.alias))

        if not matches:
            suggestions = manager.find_suggestions(search_term)
            if suggestions:
                print(
                    f"No exact match for '{search_term}'. Did you mean:",
                    file=sys.stderr,
                )
                for s in suggestions:
                    print(
                        f"  {s['alias']} (db={s['dbname']}, acct={s['account_id']})",
                        file=sys.stderr,
                    )
            else:
                print(f"No databases found matching '{search_term}'", file=sys.stderr)
            sys.exit(3)

        if len(matches) > 1:
            if args.no_prompt:
                print(
                    "Multiple matches found with --no-prompt enabled", file=sys.stderr
                )
                sys.exit(4)

            print(f"\nMultiple databases found for '{search_term}':")
            for i, match in enumerate(matches, 1):
                prod = " [PROD]" if match.env.lower() == "prod" else ""
                print(
                    f"  {i}) {match.alias} (db={match.dbname}, "
                    f"account={match.account_id}, env={match.env}){prod}"
                )

            try:
                choice = input(
                    "\nSelect database (1-{}), or 'q' to cancel: ".format(len(matches))
                ).strip()
            except KeyboardInterrupt:
                print("\nCancelled", file=sys.stderr)
                sys.exit(4)

            if choice.lower() in ("q", "quit", "exit"):
                print("Cancelled", file=sys.stderr)
                sys.exit(4)

            if not choice.isdigit() or not (1 <= int(choice) <= len(matches)):
                print("Invalid selection", file=sys.stderr)
                sys.exit(4)

            config = matches[int(choice) - 1]
        else:
            config = matches[0]

        username = manager.resolve_db_username(args.user)
        manager.connect(config, username, preview_only=args.preview)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(8)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(5)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(6)


if __name__ == "__main__":
    main()

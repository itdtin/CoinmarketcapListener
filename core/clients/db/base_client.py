class BaseClient:
    """Base client="""

    def __init__(self, host: str, port: int, user: str, password: str, db_name: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name

    def execute(self, query: str):
        pass

    def connect(self):
        pass

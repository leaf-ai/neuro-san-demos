import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from typing import Any
from typing import Dict

from neuro_san.interfaces.coded_tool import CodedTool

IDENTITY_PROVIDER_PORT = 8042


# Step 2: Create a fake "SSO server"
class SSOHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, sly_data=None, **kwargs):
        self.sly_data = sly_data
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path.startswith("/callback"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            username = params.get("username", [""])[0]

            print(f"\n✅ Received username: {username}")
            # ✅ Set the value on the shared server-level variable
            self.server.sly_data["username"] = username

            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"<h1>Hello, {username}! Login successful. You can close this window.</h1>".encode())

            # Shut down the server after receiving the login
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                b"""
                <html>
                  <head><title>Coffee Finder Advanced SAN's simulated SSO login page</title></head>
                  <body>
                    <h1>Coffee Finder Advanced SAN's simulated SSO login page</h1>
                    <form method="GET" action="/callback">
                      <label for="username">Username:</label><br>
                      <input type="text" id="username" name="username" required><br><br>
                      <button type="submit">Login</button>
                    </form>
                  </body>
                </html>
            """
            )


class IdentityManagerAPI(CodedTool):
    """
    Simulates an identity provider that can be used to authenticate users.
    """

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        :param args: None

        :param sly_data: None

        :return: Nothing - sets the username in the sly_data dictionary.
        """
        print(">>>>>>>>>>>>>>>>>>> IdentityProviderAPI >>>>>>>>>>>>>>>>>>")
        # User already logged in?
        if sly_data.get("username", None):
            # Yes, return the username
            return f"Username is: {sly_data["username"]}"

        # No, start a temporary server in the background
        server_thread = threading.Thread(target=IdentityManagerAPI.run_server, args=(sly_data,))
        server_thread.start()

        # Open a login page in a browser
        webbrowser.open(f"http://localhost:{IDENTITY_PROVIDER_PORT}/login")

        # --- Wait for login ---
        print("⏳ Waiting for user to log in...")
        while sly_data.get("username", None) is None:
            time.sleep(1)

        print(">>>>>>>>>>>>>>>>>>> DONE !!! >>>>>>>>>>>>>>>>>>")
        return f"Username is: {sly_data.get("username", None)}"

    @staticmethod
    def run_server(sly_data):
        with HTTPServer(("localhost", IDENTITY_PROVIDER_PORT), SSOHandler) as httpd:
            httpd.sly_data = sly_data  # Attach the sly_data dictionary to the server object
            print(f"🔐 SSO Server running at http://localhost:{IDENTITY_PROVIDER_PORT}")
            httpd.serve_forever()
            print("🛑 SSO Server has shut down.")

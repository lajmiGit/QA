import subprocess
import json
import os
import sys
import threading
import queue

class McpClient:
    def __init__(self, command, cwd="."):
        self.command = command
        self.cwd = cwd
        self.process = None
        self.request_id = 1
        self.response_queue = queue.Queue()
        self.running = False

    def start(self):
        """Starts the MCP server process."""
        try:
            self.process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=sys.stderr, # Forward stderr
                text=True,
                bufsize=1 # Line buffered
            )
            self.running = True
            
            # Start listener thread
            self.listener_thread = threading.Thread(target=self._listen, daemon=True)
            self.listener_thread.start()
            
            print(f"[MCP CLIENT] Connected to server at {self.cwd}")
            
            # Initial handshake (Initialize)
            self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "crewai-client", "version": "1.0"}
            })
            
            # Send initialized notification
            self._send_notification("notifications/initialized", {})
            
            return True
        except Exception as e:
            print(f"[MCP CLIENT] Failed to start server: {e}")
            return False

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()

    def list_tools(self):
        """Lists available tools from the server."""
        return self._send_request("tools/list", {})

    def call_tool(self, name, arguments):
        """Calls a tool on the server."""
        return self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })

    def _send_request(self, method, params):
        if not self.process:
            raise Exception("MCP Client not started")

        req_id = self.request_id
        self.request_id += 1
        
        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params
        }
        
        json_req = json.dumps(request)
        print(f"[MCP CLIENT] > Sending: {json_req}")
        self.process.stdin.write(json_req + "\n")
        self.process.stdin.flush()
        
        return self._wait_for_response(req_id)

    def _send_notification(self, method, params):
        if not self.process: return
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        json_req = json.dumps(request)
        self.process.stdin.write(json_req + "\n")
        self.process.stdin.flush()

    def _listen(self):
        """Reads stdout from the server line by line."""
        while self.running and self.process and self.process.stdout:
            line = self.process.stdout.readline()
            if not line:
                break
            try:
                print(f"[MCP CLIENT] < Received: {line.strip()}")
                data = json.loads(line)
                if "id" in data:
                    self.response_queue.put(data)
            except json.JSONDecodeError:
                pass # Ignore non-JSON lines

    def _wait_for_response(self, req_id, timeout=300): # 5 min timeout for long tests
        """Waits for a specific response ID."""
        # Simple polling/queue drain mechanism
        # In a robust client, we'd store pending requests in a dict.
        # Here we just drain the queue until we find ours (assuming sequential usage for now)
        
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # We peek/get from queue
                # Making this vastly simpler: Assuming sequential calls, the NEXT response 
                # that matches ID is ours.
                data = self.response_queue.get(timeout=1)
                
                if data.get("id") == req_id:
                    if "error" in data:
                        raise Exception(f"MCP Error: {data['error']}")
                    return data.get("result")
                else:
                    # Put back if not ours? Or discard?
                    # For this simple single-threaded agent usage, responses usually come in order.
                    # But notifications might interleave.
                    pass 
            except queue.Empty:
                continue
                
        raise Exception("Timeout waiting for MCP response")

# MCP Server: CSV Upload & LLM Integration Options

## Current Architecture

Your MCP server currently:
- ✅ Auto-loads CSV files from a configured directory (`csv/`)
- ✅ Provides natural language tools for data analysis
- ✅ Works with MCP clients (VS Code Copilot, Claude Desktop)
- ❌ Does NOT support dynamic CSV upload during runtime
- ❌ Does NOT include direct LLM integration

---

## Option 1: File Path Parameter (Simplest - Recommended for MVP)

### How It Works
Users specify a file path, and the MCP server loads it from the filesystem.

### Implementation
**Already 90% implemented!** Just needs better exposure:

```python
# Current code in server.py already supports this:
@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if name == "load_farm_data":
        file_path = arguments.get("file_path")  # ← Already supports custom path!
        result = await handle_load_data(arguments)
```

### User Interaction with ChatGPT

**Scenario 1: Via VS Code Copilot (MCP Integration)**
```
User: "Load the CSV file from /home/user/Downloads/new_farms.csv and analyze it"

Copilot: *Uses load_farm_data tool with file_path parameter*
         "Loaded 1,234 farms from new_farms.csv. 
          Found 6 farm types. Would you like me to classify them?"

User: "Yes, and show me statistics for dairy farms"

Copilot: *Uses classify_farms and calculate_group_statistics tools*
         "Dairy farms (Milchvieh): 456 farms
          Average animals: 145.3
          Median animals: 132.0"
```

**Scenario 2: Via Custom Web Interface + ChatGPT API**
```
User uploads CSV → Web app saves to temp directory
Web app calls ChatGPT with MCP context:
  "I have a farm CSV at /tmp/upload_abc123.csv. 
   Please load and analyze it."

ChatGPT: *Uses MCP tools to load and analyze*
         "I've analyzed your data..."
```

### Pros
- ✅ Already implemented
- ✅ Works with MCP clients immediately
- ✅ No security concerns (server-side files only)
- ✅ Simple user experience

### Cons
- ❌ User must place file on server filesystem
- ❌ Not suitable for web apps without file upload handling
- ❌ Path management complexity

---

## Option 2: Base64 CSV Content (Web-Friendly)

### How It Works
Users send CSV content encoded as Base64 string. Server decodes and processes in-memory.

### Implementation

```python
# Add new tool definition
Tool(
    name="load_farm_data_from_content",
    description=(
        "Load farm data from CSV content provided as a string. "
        "Useful for web applications where file upload is needed. "
        "Provide the CSV content directly or as base64-encoded string."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "CSV content as plain text or base64-encoded",
            },
            "encoding": {
                "type": "string",
                "enum": ["plain", "base64"],
                "default": "plain",
                "description": "Content encoding format",
            },
        },
        "required": ["content"],
    },
)

# Add handler function
async def handle_load_data_from_content(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Load farm data from CSV content string."""
    import base64
    import io
    
    content = arguments.get("content", "")
    encoding = arguments.get("encoding", "plain")
    
    try:
        # Decode if base64
        if encoding == "base64":
            content = base64.b64decode(content).decode("utf-8")
        
        # Read CSV from string
        df = pd.read_csv(io.StringIO(content))
        
        # Store in context
        data_context.raw_df = df
        data_context.data_loaded = True
        data_context.classified = False
        
        return {
            "success": True,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
        }
    except Exception as e:
        logger.error(f"Failed to load CSV content: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }
```

### User Interaction with ChatGPT

**Scenario: Web App + ChatGPT**
```javascript
// Frontend: User uploads CSV
const fileInput = document.getElementById('csvFile');
const file = fileInput.files[0];
const content = await file.text();
const base64Content = btoa(content);

// Send to ChatGPT API with MCP context
const response = await chatGPT({
    messages: [{
        role: "user",
        content: "I'm uploading a farm CSV file. Please analyze it."
    }],
    tools: [{
        name: "load_farm_data_from_content",
        content: base64Content,
        encoding: "base64"
    }]
});
```

### Pros
- ✅ Works with web applications
- ✅ No filesystem access needed
- ✅ Suitable for serverless deployments
- ✅ Clean separation of concerns

### Cons
- ❌ Size limits (MCP messages typically limited to a few MB)
- ❌ Encoding/decoding overhead
- ❌ Not suitable for very large CSVs

---

## Option 3: URL-Based Upload (Cloud-Friendly)

### How It Works
Users provide a URL to a CSV file. Server downloads and processes it.

### Implementation

```python
Tool(
    name="load_farm_data_from_url",
    description=(
        "Load farm data from a CSV file available at a URL. "
        "Supports HTTP/HTTPS URLs. Useful for cloud storage, "
        "shared files, or temporary upload services."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to CSV file (must be publicly accessible)",
            },
        },
        "required": ["url"],
    },
)

async def handle_load_data_from_url(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Load farm data from URL."""
    import aiohttp
    
    url = arguments.get("url", "")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"Failed to download: HTTP {response.status}",
                    }
                
                content = await response.text()
                df = pd.read_csv(io.StringIO(content))
                
                # Store in context
                data_context.raw_df = df
                data_context.data_loaded = True
                data_context.classified = False
                
                return {
                    "success": True,
                    "source": url,
                    "rows": len(df),
                    "columns": len(df.columns),
                }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### User Interaction with ChatGPT

```
User: "Analyze this farm data: https://my-storage.com/farms_2025.csv"

ChatGPT: *Uses load_farm_data_from_url tool*
         "Downloaded and loaded 2,345 farms from the CSV.
          I can see data from 2025 with 6 farm types..."
```

### Pros
- ✅ Works with cloud storage (S3, Google Drive, Dropbox)
- ✅ No size limits (beyond memory)
- ✅ Simple user experience
- ✅ Good for collaboration (shared links)

### Cons
- ❌ Requires public URL or signed URLs
- ❌ Security concerns (downloading arbitrary files)
- ❌ Network dependency

---

## Option 4: Multi-Session Context (Advanced)

### How It Works
Each user gets their own data context. Multiple users can upload different CSVs simultaneously.

### Implementation

```python
# Replace global context with session management
class SessionManager:
    """Manage multiple user sessions with separate data contexts."""
    
    def __init__(self):
        self.sessions: Dict[str, DataContext] = {}
    
    def get_or_create_session(self, session_id: str) -> DataContext:
        """Get existing session or create new one."""
        if session_id not in self.sessions:
            self.sessions[session_id] = DataContext()
        return self.sessions[session_id]
    
    def cleanup_old_sessions(self, max_age_minutes: int = 60):
        """Remove sessions older than max_age_minutes."""
        # Implementation for cleanup
        pass

# Global session manager
session_manager = SessionManager()

# Modify handlers to use session_id
async def handle_load_data(arguments: Dict[str, Any]) -> Dict[str, Any]:
    session_id = arguments.get("session_id", "default")
    context = session_manager.get_or_create_session(session_id)
    
    # Use context instead of global data_context
    # ... rest of implementation
```

### Pros
- ✅ Multiple users simultaneously
- ✅ Isolated data per user
- ✅ Suitable for production web apps

### Cons
- ❌ Complex implementation
- ❌ Memory management needed
- ❌ Session cleanup required

---

## Simplest LLM Integration Examples

### Example 1: ChatGPT + MCP (via API)

```python
import openai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def chat_with_mcp():
    """Chat with ChatGPT using MCP server tools."""
    
    # Connect to your MCP server
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "mcp_server.server"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize MCP connection
            await session.initialize()
            
            # Get available tools
            tools = await session.list_tools()
            
            # Chat with OpenAI using MCP tools
            client = openai.OpenAI()
            
            messages = [{
                "role": "user",
                "content": "Load the default farm CSV and tell me how many Muku farms there are"
            }]
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=[{
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    }
                } for tool in tools],
            )
            
            # Handle tool calls from ChatGPT
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    result = await session.call_tool(
                        tool_call.function.name,
                        json.loads(tool_call.function.arguments)
                    )
                    # Send result back to ChatGPT
                    # ... continue conversation
```

### Example 2: Simple Web Interface

```python
from flask import Flask, request, jsonify
import asyncio

app = Flask(__name__)

@app.route('/upload-and-analyze', methods=['POST'])
async def upload_and_analyze():
    """Upload CSV and get AI analysis."""
    
    # Get uploaded file
    csv_file = request.files['csv']
    content = csv_file.read().decode('utf-8')
    
    # Load into MCP server
    result = await handle_load_data_from_content({
        "content": content,
        "encoding": "plain"
    })
    
    if not result["success"]:
        return jsonify({"error": result["error"]}), 400
    
    # Classify farms
    await handle_classify_farms({})
    
    # Get summary
    stats = await handle_calculate_statistics({})
    
    return jsonify({
        "message": f"Loaded {result['rows']} farms",
        "statistics": stats
    })
```

### Example 3: CLI with LLM

```python
#!/usr/bin/env python3
"""Simple CLI that uses LLM to answer questions about uploaded CSV."""

import typer
from anthropic import Anthropic

app = typer.Typer()

@app.command()
def analyze(csv_file: Path):
    """Analyze CSV file using Claude."""
    
    # Load CSV
    result = asyncio.run(handle_load_data({"file_path": str(csv_file)}))
    
    if not result["success"]:
        typer.echo(f"Error: {result['error']}")
        return
    
    # Classify
    asyncio.run(handle_classify_farms({}))
    
    # Interactive Q&A with Claude
    client = Anthropic()
    
    typer.echo(f"Loaded {result['rows']} farms. Ask me anything!")
    
    while True:
        question = typer.prompt("\nQuestion")
        
        if question.lower() in ['quit', 'exit']:
            break
        
        # Get answer using MCP tools
        answer = asyncio.run(handle_answer_question({"question": question}))
        
        typer.echo(f"\nAnswer: {answer['answer']}")
```

---

## Recommended Approach: Hybrid Solution

### Phase 1: Immediate (Use Existing)
1. ✅ Keep current file path approach
2. ✅ Document it for users
3. ✅ Add better error messages
4. ✅ Users work with VS Code Copilot TODAY

### Phase 2: Add Flexibility (1-2 days)
1. Add `load_farm_data_from_content` for web apps
2. Add `load_farm_data_from_url` for cloud files
3. Keep backward compatibility

### Phase 3: Production Ready (1 week)
1. Add session management for multi-user
2. Add authentication/authorization
3. Add rate limiting
4. Deploy as web service

---

## User Experience Comparison

| Approach | Setup Time | User Experience | Best For |
|----------|-----------|-----------------|----------|
| **File Path** (Current) | 0 min | Place file on server, specify path | Local development, VS Code |
| **Base64 Content** | 2 hours | Upload via web form | Web applications |
| **URL Download** | 3 hours | Share cloud link | Collaboration, cloud storage |
| **Multi-Session** | 2 days | Upload + isolated workspace | Production SaaS |

---

## Simplest Implementation: Add Base64 Support

Here's what to add to your current `server.py`:

```python
# Add this tool to the list_tools() function
Tool(
    name="upload_csv_content",
    description=(
        "Upload CSV data directly as text content. "
        "Useful when you want to paste CSV data or upload from web interface."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "CSV content as plain text",
            },
        },
        "required": ["content"],
    },
),

# Add this handler function
async def handle_upload_csv_content(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle CSV content upload."""
    import io
    
    content = arguments.get("content", "")
    
    if not content:
        return {"success": False, "error": "No content provided"}
    
    try:
        # Parse CSV from string
        df = pd.read_csv(io.StringIO(content))
        
        # Store in global context
        data_context.raw_df = df
        data_context.data_loaded = True
        data_context.classified = False
        
        logger.info(f"Loaded CSV with {len(df)} rows from content")
        
        return {
            "success": True,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
        }
    except Exception as e:
        logger.error(f"Failed to parse CSV content: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }

# Add to call_tool() function
@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    # ... existing tools ...
    elif name == "upload_csv_content":
        result = await handle_upload_csv_content(arguments)
```

**Usage with ChatGPT:**
```
User: "Here's my CSV data:
       tvd,year,n_animals_total
       12345,2024,150
       12346,2024,200
       Please analyze it."

ChatGPT: *Uses upload_csv_content tool*
         "I've loaded your data with 2 farms..."
```

---

## Summary

**Quickest path to CSV upload + LLM:**

1. **For local/VS Code use**: Current implementation already works! Just document it.

2. **For web apps**: Add the `upload_csv_content` tool (2-3 hours work)

3. **For ChatGPT integration**: Use existing MCP client libraries (example above)

4. **Best user experience**: 
   - Users upload CSV via web form
   - Your app sends content to MCP server
   - ChatGPT/Claude analyzes via MCP tools
   - Results shown in natural language

The MCP protocol is **already designed** for this! You just need to expose the upload mechanism. 🚀

# Changelog

## Sprint 2 - June 24, 2025 (Latest Updates)

### � NEW: Command Line Interface (CLI)

#### 📱 Standalone CLI Application
- **New CLI Tool**: Added `main_cli.py` - a complete command-line interface for the RAG system
- **Simple Usage**: Research questions directly from the terminal without web interface
- **Progress Tracking**: Real-time progress updates during research process
- **Flexible Configuration**: Customizable search queries and answer rewordings via command-line options

#### 💾 Automated File Output
- **Timestamped Results**: All research results automatically saved to timestamped `.txt` files
- **Custom Output Directory**: `--output-dir` option to specify where results are saved
- **Complete Documentation**: Saved files include full research steps, evaluations, and metrics
- **Persistent Storage**: Results preserved for future reference and analysis

#### 🛠️ CLI Features
- **Argument Parsing**: Full argparse integration with help documentation
- **Verbose Mode**: `--verbose` flag for detailed progress information
- **Error Handling**: Graceful handling of missing environment variables and API errors
- **Convenience Script**: `run_cli.sh` wrapper script for easy execution

#### 📋 CLI Usage Examples
```bash
# Basic usage
./run_cli.sh "What are the benefits of renewable energy?"

# Advanced configuration
./run_cli.sh "How does AI work?" --searches 5 --rewordings 2 --verbose --output-dir ./research
```

#### 🏗️ Architecture Benefits
- **Code Reuse**: CLI leverages existing RAG system without duplication
- **Separation of Concerns**: Clean separation between web and CLI interfaces
- **Consistent Results**: Same research quality as web interface
- **Easy Maintenance**: Shared core functionality between interfaces

### �🎯 Major UI/UX Improvements

#### 🏷️ Research Query Terminology
- **Changed "Steps" to "Queries"**: Updated UI terminology from "Research Process" to "Research Queries" for better clarity
- **Query-Focused Display**: Each research step now clearly labeled as "Query X" instead of "Step X"
- **Improved User Understanding**: Better communication of what each research phase represents

#### 📊 Enhanced Quality Assessment
- **Judge Score Display**: AI quality assessment now appears below the research queries section for better flow
- **Improved Layout**: Moved evaluation metrics to appear after users can review the research process
- **Quality Metrics**: Detailed scoring for accuracy, completeness, relevance, clarity, and confidence
- **Visual Score Representation**: Color-coded overall scores with detailed metric breakdowns

#### ⚙️ Configurable Research Settings
- **Customizable Search Queries**: Users can now set the number of search queries (1-10, default: 3)
- **Adjustable Answer Iterations**: Configurable maximum answer improvement attempts (1-5, default: 3)
- **Real-time Settings**: Settings applied immediately to each research session
- **Advanced Research Options**: Power users can increase complexity for more thorough research

#### 🎨 Simplified & Clean Styling
- **Streamlined CSS**: Dramatically reduced CSS from 925+ lines to ~200 lines
- **Modern Minimalism**: Cleaner, more focused design without unnecessary complexity
- **Better Performance**: Faster page loads with simplified stylesheets
- **Maintainable Code**: Much easier to maintain and customize styling

#### 🔧 Technical Backend Improvements
- **Dynamic Query Generation**: LLM client now accepts configurable number of queries
- **Evaluation Loop Enhancement**: Configurable number of answer improvement iterations
- **Parameter Passing**: Full integration of user settings through the entire pipeline
- **Improved Response Structure**: Better data flow from frontend settings to backend processing

### 📸 Documentation Enhancement
- **Screenshot Added**: Added application screenshot (`imgs/image.png`) to README
- **Visual Documentation**: Users can now see the interface before trying the application
- **Improved Onboarding**: Better first impression with visual representation

### 🔄 Architecture Refinements
- **Settings Integration**: Seamless integration of user preferences into research pipeline
- **Frontend-Backend Communication**: Enhanced WebSocket message structure for settings
- **Parameter Validation**: Proper validation of user input ranges for settings
- **Default Value Management**: Sensible defaults with user override capabilities

### 📁 Updated File Structure
```
├── src/
│   ├── models.py          # Enhanced with evaluation models
│   ├── llm_client.py      # Configurable query generation
│   ├── search_client.py   # Search client (unchanged)
│   └── rag_system.py      # Enhanced with configurable parameters
├── templates/
│   └── index.html         # Settings section and improved layout
├── static/
│   ├── css/
│   │   └── styles.css     # Simplified from 925+ to ~200 lines
│   └── js/
│       └── app.js         # Enhanced settings handling
├── imgs/
│   └── image.png          # Application screenshot
└── ...
```

### 🎯 User Experience Improvements
- **Intuitive Controls**: Clear labels and hints for all settings
- **Immediate Feedback**: Settings take effect on next research query
- **Progressive Disclosure**: Advanced settings available but not overwhelming
- **Better Information Architecture**: Logical flow from answer → queries → evaluation

---

## Sprint 1 - June 24, 2025

### ✅ Completed Features

#### 🏗️ Architecture Refactoring
- **File Modularization**: Split the monolithic RAG system into multiple files to comply with the 300-line limit requirement:
  - `src/models.py` (62 lines) - Pydantic models for data validation
  - `src/llm_client.py` (116 lines) - HTTP client for LLM API requests
  - `src/search_client.py` (77 lines) - Tavily search client
  - `src/rag_system.py` (202 lines) - Main orchestration logic

#### 🔧 Technical Implementation
- **Removed OpenAI Library**: Replaced OpenAI SDK with pure `requests` library for HTTP calls
- **OpenAI-Compatible API Support**: Maintained compatibility with OpenAI API format while using only HTTP requests
- **Environment Configuration**: All API keys and URLs configured via `.env` file
- **Session Logging**: Each research session logs to individual files in `logs/` directory

#### 🎨 User Interface
- **FastAPI Web Application**: Modern web interface with real-time progress updates
- **WebSocket Integration**: Live progress tracking during research process
- **Responsive Design**: Mobile-friendly UI with gradient styling
- **Interactive Results**: Expandable research steps with detailed analysis

#### 🔍 RAG Pipeline
- **Multi-Query Generation**: LLM generates multiple search queries for comprehensive research
- **Tavily Search Integration**: Web search using direct HTTP requests to Tavily API
- **Research Analysis**: Each search result analyzed and synthesized by LLM
- **Final Synthesis**: All research combined into comprehensive answer

#### 📊 Data Models
- **Pydantic Validation**: All data structures use Pydantic for type safety
- **Progress Tracking**: Real-time updates sent via WebSocket
- **Research Steps**: Detailed logging of each research phase
- **Session Management**: Unique session IDs for tracking and logging

### 🛠️ Dependencies
- `fastapi==0.104.1` - Web framework
- `uvicorn==0.24.0` - ASGI server
- `websockets==12.0` - Real-time communication
- `python-dotenv==1.0.0` - Environment variable management
- `requests==2.31.0` - HTTP client (only HTTP library used)
- `pydantic==2.5.0` - Data validation
- `aiofiles==23.2.1` - Async file operations
- `jinja2==3.1.2` - HTML templating

### 📁 Project Structure
```
├── src/
│   ├── models.py           # Data models
│   ├── llm_client.py       # LLM HTTP client
│   ├── search_client.py    # Tavily search client
│   └── rag_system.py       # Main orchestration
├── templates/
│   └── index.html          # Web UI
├── logs/                   # Session logs
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── README.md              # Documentation
```

### 🎯 Key Requirements Met
- ✅ Files under 300 lines each
- ✅ Only `requests` library for HTTP calls
- ✅ OpenAI-compatible LLM support
- ✅ Tavily search integration
- ✅ FastAPI with WebSocket UI
- ✅ Session logging to files
- ✅ Pydantic data modeling
- ✅ Environment-based configuration

### 🚀 Next Sprint Planning
- [ ] Add error handling and retry logic
- [ ] Implement rate limiting for API calls
- [ ] Add result caching mechanism
- [ ] Create API documentation
- [ ] Add unit tests
- [ ] Performance optimization
- [ ] Add authentication for production use

### 🐛 Bug Fixes - June 24, 2025 (Evening)

#### WebSocket Progress Callback Issue
- **Fixed async callback warning**: Updated `_send_progress_update` to be async and properly awaited
- **Resolved RuntimeWarning**: "coroutine 'websocket_endpoint.<locals>.progress_callback' was never awaited"
- **Improved error handling**: Better async flow in progress updates

#### Process Management
- **Added stop.sh script**: Easy way to kill running FastAPI/uvicorn processes
- **Multiple kill methods**: Process name, port-based, and backup killing strategies
- **Clean shutdown**: Prevents hanging processes during development

#### Environment Setup
- **Auto-install uv**: `run.sh` now automatically installs uv via pip if not found
- **Better error messages**: Clear instructions when uv installation fails
- **Virtual environment fix**: Uses `.venv` directory (uv default) instead of `venv`

### 🔧 Technical Details
- Updated all `_send_progress_update` calls to use `await`
- Added `./stop.sh` script for clean process termination
- Enhanced `./run.sh` with automatic uv installation fallback
- Fixed virtual environment path consistency

### 📁 New Files
- `stop.sh` - Process termination script

### ✨ Major UI Enhancement - June 24, 2025 (Late Evening)

#### 🎨 Professional UI Redesign
- **Modern Design System**: Complete UI overhaul with professional gradient backgrounds and glass-morphism effects
- **Typography Enhancement**: Added Inter and Fira Code fonts for better readability
- **Advanced Animations**: Smooth transitions, hover effects, and loading animations
- **Responsive Design**: Mobile-first approach with breakpoints for all screen sizes

#### 📎 File Upload Capability
- **File Attachment Feature**: Users can now attach text files (.txt, .md, .json, .csv, .xml, .py, .js, .html, .css)
- **File Preview**: Real-time preview of uploaded file content
- **File Size Validation**: 1MB file size limit with user-friendly error messages
- **Content Integration**: File content automatically appended to research queries

#### 📝 Markdown Support & Code Highlighting
- **Full Markdown Rendering**: Research answers displayed with rich markdown formatting
- **Syntax Highlighting**: Code blocks with copy-to-clipboard functionality
- **Interactive Elements**: Expandable sections, animated progress indicators
- **Copy Code Feature**: One-click code copying with visual feedback

#### 🏗️ Modular Architecture
- **Separated Concerns**: Split HTML, CSS, and JavaScript into separate files
- **Static File Serving**: FastAPI serves CSS/JS assets efficiently
- **Component-Based JS**: Object-oriented JavaScript with clean class structure
- **Maintainable Code**: Each file focused on single responsibility

#### 🔧 Enhanced User Experience
- **Real-time Progress**: Animated progress bars with step-by-step updates
- **Session Management**: Download and share session capabilities
- **Auto-resize Input**: Textarea automatically adjusts to content
- **Keyboard Shortcuts**: Enter to submit, Shift+Enter for new lines
- **Error Handling**: Comprehensive error states with helpful messages

#### 📁 New File Structure
```
static/
├── css/
│   └── styles.css      # Professional UI styles (400+ lines)
└── js/
    └── app.js          # Modern JavaScript application (300+ lines)
templates/
└── index.html          # Clean HTML structure (80 lines)
```

#### 🎯 Technical Improvements
- **WebSocket Optimization**: Better async handling and reconnection logic
- **Markdown Integration**: markdown-it library for rich text rendering
- **Code Highlighting**: highlight.js for syntax-highlighted code blocks
- **Icon System**: Font Awesome icons throughout the interface
- **Performance**: Optimized loading and rendering performance

### 📊 Enhanced Progress Tracking - June 24, 2025 (Night)

#### 🔍 Detailed Progress Updates
- **Granular Step Tracking**: Progress now shows 6 detailed steps instead of 4 generic ones
- **Real-time Activity**: Specific messages for each action (searching, analyzing, synthesizing)
- **Search Progress**: Individual progress for each search query with truncated preview
- **Analysis Tracking**: Step-by-step analysis progress with source count information
- **Synthesis Details**: Detailed compilation and finalization messages

#### 📱 Enhanced UI Progress Display
- **Activity Log**: Live activity log showing timestamped progress updates
- **Visual Enhancements**: Emoji indicators and status-specific progress bar colors
- **Step Indicators**: Clear step numbering with visual progress badges
- **Auto-scrolling**: Automatic scrolling to show latest progress updates
- **Responsive Messages**: Truncated long queries to fit UI elegantly

#### 🎨 Progress Visual Improvements
- **Status Colors**: Different progress bar colors for different phases
  - 🔍 Orange for searching
  - 🧠 Blue for analyzing  
  - 🔗 Purple for synthesizing
  - ✅ Green for completion
- **Activity Animations**: Enhanced spinner animations for active states
- **Smooth Transitions**: Fade-in animations for new log entries
- **Clean Completion**: Progress log automatically clears on completion

#### 📋 Detailed Progress Messages
```
🤖 Analyzing your question and generating search queries...
✅ Generated 3 targeted search queries
🔍 Searching for: "latest AI developments 2025..." (1/3)
📄 Found 3 results for search 1/3
🔬 Analyzing results for: "AI developments..." (1/3)
📊 Processing 3 sources for analysis 1/3
✅ Completed analysis 1/3
🔗 Synthesizing comprehensive answer from all research...
📝 Compiling insights from 3 research analyses...
✨ Finalizing comprehensive research report...
🎉 Research completed! Comprehensive answer ready.
```

#### 🔧 Technical Implementation
- **6-Step Process**: More granular progress tracking (was 4, now 6 steps)
- **Enhanced WebSocket**: Richer progress data with status codes and detailed messages
- **Activity Logging**: In-memory activity log with automatic cleanup
- **Status Management**: Better state management for different research phases

# Kuma Monitor CLI

A Python script to check Uptime Kuma monitor status via command line with automatic updates.

![Kuma Monitor Demo](demo.png)

## Features

- **🔄 Auto-update** every 30 seconds (configurable)
- **🎨 Colored output** for better visualization
- **📊 Table format** similar to docker stats
- **⚙️ Configurable** via environment variables
- **📱 Clean interface** with optional header and countdown
- **🛡️ Robust error handling** with retry mechanism and exponential backoff
- **🌐 DNS resolution recovery** for network connectivity issues

## Installation

No installation required! The script is completely standalone and only uses Python standard library modules plus `requests` (which is usually pre-installed).

```bash
# If requests is not installed (rare)
pip install requests
```

## Configuration

### Environment Variables

The script can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `KUMA_ENDPOINT` | `https://your-kuma-server.com/metrics` | Uptime Kuma metrics endpoint |
| `KUMA_API_KEY` | `your-api-key-here` | API key for authentication |
| `KUMA_UPDATE_INTERVAL` | `30` | Update interval in seconds |
| `KUMA_SHOW_HEADER` | `true` | Show table header (true/false) |
| `KUMA_SHOW_COUNTDOWN` | `true` | Show countdown timer (true/false) |
| `KUMA_SHOW_HISTORY` | `true` | Show history bars (true/false) |
| `KUMA_HISTORY_LENGTH` | `60` | Number of history entries to keep and display as squares |
| `KUMA_MAX_RETRIES` | `3` | Maximum number of retry attempts for failed requests |
| `KUMA_RETRY_DELAY` | `5` | Base delay in seconds between retry attempts (exponential backoff) |

### Setup Options

#### Option 1: Using .env file
```bash
# Create a .env file with your configuration
cat > .env << EOF
KUMA_ENDPOINT=https://your-endpoint.com/metrics
KUMA_API_KEY=your-api-key
KUMA_UPDATE_INTERVAL=30
KUMA_SHOW_HEADER=true
KUMA_SHOW_COUNTDOWN=true
KUMA_SHOW_HISTORY=true
KUMA_HISTORY_LENGTH=60
KUMA_MAX_RETRIES=3
KUMA_RETRY_DELAY=5
EOF
```

#### Option 2: Using export commands
```bash
export KUMA_ENDPOINT="https://your-endpoint.com/metrics"
export KUMA_API_KEY="your-api-key"
export KUMA_UPDATE_INTERVAL="60"
export KUMA_SHOW_HEADER="false"
export KUMA_SHOW_COUNTDOWN="false"
export KUMA_MAX_RETRIES="5"
export KUMA_RETRY_DELAY="3"
```

## Usage

```bash
./kuma-monitor.py
```

### Standalone Execution

The script is completely standalone:
- Python 3.6+ (standard library only)
- `requests` library (usually pre-installed)
- No external dependencies
- No installation required

## Error Handling

The script includes robust error handling for various network issues:

- **DNS Resolution Errors**: Automatically retries with exponential backoff
- **Connection Timeouts**: Handles temporary network issues
- **Server Errors**: Retries on 5xx status codes
- **Rate Limiting**: Respects 429 status codes with backoff

### Retry Strategy

- **Exponential Backoff**: Delay increases with each retry attempt
- **Configurable Retries**: Set `KUMA_MAX_RETRIES` to control attempts
- **Graceful Degradation**: Continues monitoring even after temporary failures
- **Clear Error Messages**: Different colors for different error types

## Examples

### Minimal output (no header, no countdown)
```bash
export KUMA_SHOW_HEADER="false"
export KUMA_SHOW_COUNTDOWN="false"
./kuma-monitor.py
```

### Custom update interval
```bash
export KUMA_UPDATE_INTERVAL="60"
./kuma-monitor.py
```

### Custom endpoint with aggressive retry
```bash
export KUMA_ENDPOINT="https://your-uptime-kuma.com/metrics"
export KUMA_API_KEY="your-api-key"
export KUMA_MAX_RETRIES="5"
export KUMA_RETRY_DELAY="2"
./kuma-monitor.py
```

### Conservative retry settings for unstable networks
```bash
export KUMA_MAX_RETRIES="10"
export KUMA_RETRY_DELAY="10"
./kuma-monitor.py
```

## Status Colors

- 🟢 **Green**: UP
- 🔴 **Red**: DOWN
- 🟡 **Yellow**: PENDING
- 🔵 **Blue**: MAINTENANCE

## Error Colors

- 🟡 **Yellow**: Connection/DNS errors (retrying)
- 🔴 **Red**: Fatal errors (will retry on next cycle)

## Exit

Press `Ctrl+C` to exit gracefully.

## Troubleshooting

### Common Issues

1. **DNS Resolution Errors**: The script will automatically retry with exponential backoff
2. **Network Timeouts**: Temporary network issues are handled gracefully
3. **API Key Issues**: Check your `KUMA_API_KEY` configuration
4. **Endpoint Issues**: Verify your `KUMA_ENDPOINT` URL

### Debug Mode

To see more detailed error information, you can modify the script to increase verbosity or check the network connectivity manually:

```bash
# Test endpoint connectivity
curl -H "Authorization: Bearer your-api-key" https://your-endpoint.com/metrics
```

License
-------

© 2025 [Acauã Montiel](http://acauamontiel.com.br)

[MIT License](http://acaua.mit-license.org/)
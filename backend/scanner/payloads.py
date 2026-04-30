SQLI_PAYLOADS = [
    "' OR '1'='1",
    "admin' --",
    "1; DROP TABLE users"
]

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "\"><img src=x onerror=alert(1)>",
]

SENSITIVE_ENDPOINTS = [
    "/admin",
    "/.env",
    "/.git",
    "/config.php",
    "/wp-config.php",
]

def get_headers_to_check():
    return [
        "Strict-Transport-Security",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Content-Security-Policy"
    ]

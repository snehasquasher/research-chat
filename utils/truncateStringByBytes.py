def truncate_string_by_bytes(s: str, bytes: int) -> str:
    encoded_str = s.encode('utf-8')
    truncated_str = encoded_str[:bytes]
    return truncated_str.decode('utf-8', 'ignore')

#!/usr/bin/env python3.8

def stream_key_from_id(id: int):

    """Outputs stream key by game id so all stream names follow the same format."""

    return f"game-{id}"

def parse_stream_output(output: list):

    """Parses the gibberish returned by a redis stream to readable gibberish."""

    [[_, items]] = output
    return [item[1] for item in items]

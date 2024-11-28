import trufnetwork_sdk_c_bindings.exports as truf_sdk

def generate_stream_id(name: str) -> str:
    """
    Create a hash from a name, to be used as a stream ID. Must be unique among a dataprovider's streams.
    """
    return truf_sdk.GenerateStreamId(name)

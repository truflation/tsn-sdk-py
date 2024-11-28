from typing import Dict, List, Union, Optional
import trufnetwork_sdk_c_bindings.exports as truf_sdk
import trufnetwork_sdk_c_bindings.go as go

class TNClient:
    def __init__(self, url: str, token: str):
        self.client = truf_sdk.NewClient(url, token)

    def deploy_stream(self, stream_id: str, stream_type: int = truf_sdk.StreamTypePrimitive, wait: bool = True) -> str:
        """ 
        Deploy a stream with the given stream ID and stream type.
        If wait is True, it will wait for the transaction to be confirmed.
        Returns the transaction hash.
        """
        deploy_tx_hash = truf_sdk.DeployStream(self.client, stream_id, stream_type)
        if wait:
            truf_sdk.WaitForTx(self.client, deploy_tx_hash)
        return deploy_tx_hash

    def stream_exists(self, stream_id: str, data_provider: Optional[str] = None) -> bool:
        """ 
        Check if a stream with the given stream ID exists.
        Returns True if the stream exists, False otherwise.
        """

        # workaround as can't accept nullable type
        if data_provider is None:
            data_provider = ""

        return truf_sdk.StreamExists(self.client, stream_id, data_provider)

    """ 
        Initialize a stream with the given stream ID.
        If wait is True, it will wait for the transaction to be confirmed.
        Returns the transaction hash.
    """
    def init_stream(self, stream_id: str, wait: bool = True) -> str:
        init_tx_hash = truf_sdk.InitStream(self.client, stream_id)
        if wait:
            truf_sdk.WaitForTx(self.client, init_tx_hash)
        return init_tx_hash


    def insert_records(self, stream_id: str, records: List[Dict[str, Union[str, float, int]]], wait: bool = True) -> str:
        """ 
        Insert records into a stream with the given stream ID.
        If wait is True, it will wait for the transaction to be confirmed.
        Returns the transaction hash.
        """
        dates = [record['date'] for record in records]
        values = [record['value'] for record in records]
        insert_tx_hash = truf_sdk.InsertRecords(
            self.client,
            stream_id,
            go.Slice_string(dates),
            go.Slice_float64(values)
        )
        if wait:
            truf_sdk.WaitForTx(self.client, insert_tx_hash)
        return insert_tx_hash

    def get_records(self, stream_id: str,
                    data_provider: Optional[str] = None,
                    date_from: Optional[str] = None,
                    date_to: Optional[str] = None,
                    frozen_at: Optional[str] = None,
                    base_date: Optional[str] = None) -> List[Dict[str, any]]:
        """ 
        Get records from a stream with the given stream ID.
        Returns a list of records.

        Parameters:
            stream_id: str
                The stream ID to get records from.
            data_provider: Optional[str]
                The data provider to get records from. Format: hex string
            date_from: Optional[str]
                The start date to get records from. Format: YYYY-MM-DD
            date_to: Optional[str]
                The end date to get records from. Format: YYYY-MM-DD
            frozen_at: Optional[str]
                The frozen date used to get records from. Format: YYYY-MM-DD
            base_date: Optional[str]
                The base date used to get records from. Format: YYYY-MM-DD
        """


        # workaround as can't accept nullable type
        if data_provider is None:
            data_provider = ""
        if date_from is None:
            date_from = ""
        if date_to is None:
            date_to = ""
        if frozen_at is None:
            frozen_at = ""
        if base_date is None:
            base_date = ""

        # convert goSliceOfMaps to list of dicts
        goSliceOfMaps = truf_sdk.GetRecords(self.client, stream_id, data_provider, date_from, date_to, frozen_at, base_date)
        result = []
        for record in goSliceOfMaps:
            result.append(dict(record.items()))

        # as expected by the caller
        return result

    def execute_procedure(self, stream_id: str, procedure: str, args: List[List[Union[str, float, int]]], wait: bool = True) -> str:
        """ 
        Execute an arbitrary procedure with the given stream ID.
        If wait is True, it will wait for the transaction to be confirmed.
        Returns the transaction hash.

        Parameters:
            stream_id: str
                The stream ID to execute the procedure on.
            procedure: str
                The procedure to execute.
            args: List[List[Union[str, float, int]]]
                The arguments to pass to the procedure.
            wait: bool
                Whether to wait for the transaction to be confirmed.
        """

        # transpose the args so that it's a list of lists of strings
        transposed_args = list(map(list, zip(*args)))
        # associate the type depending if it's a string, float or int
        # for example, Slice_string for strings, Slice_float64 for floats
        variadic_args = []
        for arg in transposed_args:
            if all(isinstance(item, str) for item in arg):
                variadic_args.append(truf_sdk.ArgsFromStrings(go.Slice_string(arg)))
            elif all(isinstance(item, float) for item in arg):
                variadic_args.append(truf_sdk.ArgsFromFloats(go.Slice_float64(arg)))
            else:
                raise ValueError(f"Unsupported argument type: {arg}")

        insert_tx_hash = truf_sdk.ExecuteProcedure(
            self.client,
            stream_id,
            procedure,
            *variadic_args
        )
        if wait:
            truf_sdk.WaitForTx(self.client, insert_tx_hash)
        return insert_tx_hash

    def wait_for_tx(self, tx_hash: str) -> None:
        truf_sdk.WaitForTx(self.client, tx_hash)



from phi.tools import Toolkit


class DataSaveToolkit(Toolkit):
    def __init__(self, adapter):
        super().__init__(name="data_save_tool")
        self.ad = adapter
        self.register(self.data_save_tool)

    def data_save_tool(self, context: str) -> str:
        """This tool takes a string which is a filename and saves it to a datastore"""
        print(context)
        try:
            self.ad.add_to_datastore(context)
            return "Data saved successfully."
        except Exception as e:
            return f"Error saving data: {str(e)}"
        

class DataQueryToolkit(Toolkit):
    def __init__(self, adapter):
        super().__init__(name="data_query_tool")
        self.ad = adapter
        self.register(self.data_query_tool)

    def data_query_tool(self, query: str) -> str:
        """This tool takes the user's original query as a string which is used to query against a datastore"""
        print(query)
        try:
            result = self.ad.query_datastore(query)
            print(f"result from query: {result}")
            return result
        except Exception as e:
            return f"Error saving data: {str(e)}"

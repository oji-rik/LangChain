using Newtonsoft.Json;

namespace AzureOpenAI_Net481_FunctionCalling.Models
{
    public class FunctionResponse
    {
        [JsonProperty("request_id")]
        public string RequestId { get; set; }

        [JsonProperty("result")]
        public object Result { get; set; }

        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("error")]
        public string Error { get; set; }

        public static FunctionResponse CreateSuccess(string requestId, object result)
        {
            return new FunctionResponse
            {
                RequestId = requestId,
                Result = result,
                Success = true,
                Error = null
            };
        }

        public static FunctionResponse CreateError(string requestId, string error)
        {
            return new FunctionResponse
            {
                RequestId = requestId,
                Result = null,
                Success = false,
                Error = error
            };
        }
    }
}
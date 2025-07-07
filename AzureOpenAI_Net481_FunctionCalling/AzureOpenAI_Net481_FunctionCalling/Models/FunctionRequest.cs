using Newtonsoft.Json;
using System.Collections.Generic;

namespace AzureOpenAI_Net481_FunctionCalling.Models
{
    public class FunctionRequest
    {
        [JsonProperty("function_name")]
        public string FunctionName { get; set; }

        [JsonProperty("arguments")]
        public Dictionary<string, object> Arguments { get; set; }

        [JsonProperty("request_id")]
        public string RequestId { get; set; }
    }
}
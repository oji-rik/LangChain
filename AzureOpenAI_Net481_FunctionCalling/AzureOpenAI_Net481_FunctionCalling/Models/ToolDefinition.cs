using Newtonsoft.Json;
using System.Collections.Generic;

namespace AzureOpenAI_Net481_FunctionCalling.Models
{
    public class ToolDefinition
    {
        [JsonProperty("name")]
        public string Name { get; set; }

        [JsonProperty("description")]
        public string Description { get; set; }

        [JsonProperty("parameters")]
        public ParametersSchema Parameters { get; set; }
    }

    public class ParametersSchema
    {
        [JsonProperty("type")]
        public string Type { get; set; }

        [JsonProperty("properties")]
        public Dictionary<string, PropertySchema> Properties { get; set; }

        [JsonProperty("required")]
        public string[] Required { get; set; }
    }

    public class PropertySchema
    {
        [JsonProperty("type")]
        public string Type { get; set; }

        [JsonProperty("description")]
        public string Description { get; set; }

        [JsonProperty("items")]
        public PropertySchema Items { get; set; }
    }

    public class ToolsResponse
    {
        [JsonProperty("tools")]
        public List<ToolDefinition> Tools { get; set; }
    }
}
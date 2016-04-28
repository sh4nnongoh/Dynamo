using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Dynamo.DynamoSandbox;

namespace DynamoSandboxWrapper
{
    public class DynamoCSharpWrapper
    {
        //protected static DynamoSandbox.Program DynSandbox { get; set; }

        public static void Initialize()
        {
            string[] arg = new string[] { "" };
            DynamoSandbox.Program.Main(arg);
        }

    }
}

devagent/
├── agent/
│   ├── planner.py        # 需求理解 / 任务拆解
│   ├── coder.py          # 代码生成
│   ├── tester.py         # 测试生成与执行
│   ├── debugger.py       # Bug 分析与修复
│   ├── reflector.py      # 反思模块（加分）
│   └── agent_loop.py     # 核心控制逻辑
│
├── tools/
│   ├── run_tests.py
│   ├── apply_patch.py
│   ├── read_file.py
│   └── search_code.py
│
├── benchmarks/
│   ├── humaneval_runner.py
│   ├── mbpp_runner.py
│   └── swebench_runner.py
│
├── cli.py                # CLI 入口
├── prompts/
│   ├── plan.txt
│   ├── code.txt
│   ├── test.txt
│   ├── debug.txt
│   └── reflect.txt
│
├── results/
│   └── evaluation.json
└── README.md

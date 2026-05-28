
# Orchestration

We now include some lightweight tools to orchestrate simple pipelines via hamilton.

To get started, take a look at the [example](./src/lf_py_stack/orchestration/example.py), and then run it with python, providing paramters as needed.

Typical commands are:
```bash
python ./src/lf_py_stack/orchestration/example.py --help
python ./src/lf_py_stack/orchestration/example.py list
python ./src/lf_py_stack/orchestration/example.py run -s all
```

And
```bash
python ./src/lf_py_stack/orchestration/example.py run -s all -s step_b:'hello world' -o step_f
```

Will produce the following output:

```raw
Running the following steps:
         ╷
  Step   │ Description
 ════════╪════════════════════════════════════════════════════════════════════════════
  step_a │ A dummy step
 ────────┼────────────────────────────────────────────────────────────────────────────
  step_b │ Step that uses env vars, cli arguments and previous results
 ────────┼────────────────────────────────────────────────────────────────────────────
  step_c │ To denote the sequence, make steps depende on previous ones via arguments.
         │ You do not _have to use_ `step_b` in here.
 ────────┼────────────────────────────────────────────────────────────────────────────
  step_d │ Check status of previous steps to propagate errors and skip steps
 ────────┼────────────────────────────────────────────────────────────────────────────
  step_e │ We can also log everything we do (to send via email) and run cli commands
         ╵

Hello from step_a
Hello from step_b
Current shell: /bin/zsh
Cli Arguments to this step: hello world
Previous step result: All good
Hello from step_c
Hello from step_d
Hello from step_e
                              Orchestration run complete
         ╷        ╷
  Step   │ Status │ Log
 ════════╪════════╪═══════════════════════════════════════════════════════════════════
  step_a │ PASS   │ All good
 ────────┼────────┼───────────────────────────────────────────────────────────────────
  step_b │ PASS   │ Also all good
 ────────┼────────┼───────────────────────────────────────────────────────────────────
  step_c │ FAIL   │ Something went wrong
 ────────┼────────┼───────────────────────────────────────────────────────────────────
  step_d │ SKIP   │ Skipped due to failure in step_c
 ────────┼────────┼───────────────────────────────────────────────────────────────────
  step_e │ PASS   │ total 392
         │        │ -rw-r--r--@ 1 paul  staff    4140 May 27 17:22 CHANGELOG.md
         │        │ drwxr-xr-x@ 3 paul  staff      96 Apr 22 16:41 dist
         │        │ -rw-r--r--  1 paul  staff     677 Apr  3 20:43 docker-compose.yml
         │        │ -rw-r--r--  1 paul  staff    3303 Apr  3 20:43 Dockerfile
         │        │ drwxr-xr-x  7 paul  staff     224 May  5 09:41 docs
         │        │ -rwxr-xr-x  1 paul  staff    1482 Feb  4 16:54 entrypoint.sh
         │        │ -rw-r--r--  1 paul  staff    1076 Dec  8 14:01 LICENSE
         │        │ -rw-r--r--  1 paul  staff    1661 May  5 09:41 pyproject.toml
         │        │ -rw-r--r--@ 1 paul  staff    2685 May 27 14:07 README.md
         │        │ -rw-r--r--  1 paul  staff    6238 May  4 10:19 requirements.txt
         │        │ drwxr-xr-x@ 3 paul  staff      96 Mar 19 11:19 src
         │        │ -rw-r--r--  1 paul  staff  157699 May  5 09:41 uv.lock
         │        │
 ────────┼────────┼───────────────────────────────────────────────────────────────────
  step_f │ OMIT   │ Did not run (as requested via CLI)
         ╵
```

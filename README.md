# gptdo-tool

A command-line tool which takes instructions in plain english and uses AI to suggest and run terminal commands based on the specified output 

## Configuration

1. Clone the repository to your desired location
2. Create a symlink to bin/gptdo somewhere on your path, e.g. `ln -s ./bin/gptdo /usr/bin/gptdo`
3. Create directory `~/.gptdo` or run `gptdo` to have it created for you
4. Create `~/.gptdo/.env` with the following contents:

```env
OPENAI_API_KEY=your-openai-api-key
GPT_MODEL=gpt-4o
```

## Limitations

The `gptdo` tool has a couple key limitations:

1. Non-persistent shell environment: If gptdo tried to run the commands `cd ~/newdir` then `touch new_file` in order, it will NOT touch `new_file` in `newdir`, but in whatever working directory you ran `gptdo` in, because each command is run in a new subshell. This also means that any changes `gptdo` makes to your current environment (such as PWD or any other environment variables) will be gone when `gptdo` is done running.
2. No stdin pipe: If a command that is run by `gptdo` requires user input, such as a `y/n` prompt, it will get stuck, as stdin is not currently forwarded to the user.

## Usage

### In-line prompt

Use the `-p` flag to ask a question directly in your command. This will immediately kick-off the processing of the response, and will apply special formatting to your conversation history like the default `gptdo` mode does.

Example:

```log
$> gptdo -p "Give me an interesting fact in 5 words or less"
 > Honey never spoils over time. 
```

### Auto-approve commands

Use the `-y` flag to automatically run any recommended commands without being asked for approval first. Use at your own risk.

### Special context files

You can use `gptdo -F file1 file2 file3` to add extra context to the chat. These files can contain anything - it could be a file you want to do some code analysis on, extra prompt instructions that you've saved to a file for ease of re-use, or environment configurations for prompts which require extra knowledge such as a database endpoint.

If a specified file does not exist relative to your current working directory, it will check to see if the file exists within `~/.gptdo/contexts`. If you have some special context you will re-use frequently but don't need for every use of `gptdo`, it is recommended to create it as a file in `~/.gptdo/contexts`.

Example:
1. `nano ~/.gptdo/contexts/my_db`
2. Contents:

```txt
MySQL Database Info:
 - host: db.myapp.com
 - user: remote
 - password: prompt for password
 - db_name: my_app_db
 - notes:
   - The remote user for this DB has read-only access
```

3. `gptdo -F my_db -p "Open a connection to my database"`
4. GPT will prompt you to run a mysql command which will connect you to the db as laid out in the `my_db` file.

### Raw output

Use the `-r` flag in conjuction with `-p` to get gptdo's commands as raw output, and omit any other output. This makes it possible to run command directly in your shell using `eval`.

Example:

- `$> eval $(gptdo -r -p "change my directory to my home directory")`
- gptdo will print `cd ~` and that will be evaluated, thus moving you to your home directory.
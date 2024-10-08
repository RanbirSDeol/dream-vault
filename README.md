# Dream Vault - Overview

Dream Vault is a command-line tool for managing and logging your dreams. It offers functionality for creating, navigating, and modifying dream entries, checking statistics, backing up and syncing data, and more. It also gives you full control of your files which will stay on your PC, and are not accessisible by anyone else.

## Features

- **Create and Manage Entries**: Add, read, and edit your dream entries.
- **Backup and Sync**: Keep your data secure and synchronized.
- **Clear Logs and Console**: Manage and clean your log files and console output.

## Configurations

### Modifying Paths

You can modify the paths for logs, syncs, templates, journal, and backups in the `dream-vault/src/journal.py` file:

- **Lines 34-40**: Update the locations of logs, syncs, templates, journal, and backups.
- **Line 68**: Choose your preferred text editor.

# Dream-Vault - Setup and Run Instructions

## Prerequisites

Ensure you have the following installed on your system:
- [Python 3](https://www.python.org/downloads/) 
- [Git](https://git-scm.com/downloads)

## Step 1: Clone the Repository

First, you need to clone the repository from GitHub. Open your terminal and run:

```bash
git clone https://github.com/RanbirSDeol/dream-vault
```

## Step 2: Navigate to the Project Directory

```bash
cd dream-vault
```

## Step 3: Create Necessary Directories

Make sure you are inside the /dream-vault directory when doing this. You 
can also choose to change the location of journal if you wish, but you must
go into dream-vault/src/journal.py and edit the directories path.

```bash
mkdir backups
mkdir journal
```
## Step 4: Execute Program

Navigate to the source folder, and execute the program
(You can either use python3 or python, depending on your system configuration.)

```bash
cd src
python3 journal.py
```

## Step 5: Use 'help' Command To Navigate

To figure out how to use the program, you may want to use the 'help' command,
it will help you understand what commands you can call, the rest is self explanatory.

```bash
Dream Journal Assistance

Enter a command (type 'help' for commands): help
```


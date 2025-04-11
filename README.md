# AA Helper

A CLI tool to parse, hash, verify signatures, and debug EIP-4337 UserOperations.

## Installation

```bash
# Install in editable mode
pip install -e .
```

## Usage

The tool provides several commands:

```bash
# Get help
aa --help

# Parse raw UserOp text to formatted JSON
aa parse "<raw_user_op_text>"

# Calculate UserOp hash
aa userOpHash "<raw_user_op_text>" --chainId <id> [--entrypoint <addr>]

# Recover signer (show all attempts)
aa signer "<raw_user_op_text>" --chainId <id> --signer [--entrypoint <addr>]

# Verify signer against a specific address
aa signer "<raw_user_op_text>" --chainId <id> --signer <expected_addr> [--entrypoint <addr>]

# Generate debug cast call command
aa debug "<raw_user_op_text>" --rpc-url <url>

# Generate AND execute debug cast call command
aa debug "<raw_user_op_text>" --rpc-url <url> --run
```

**Note:** Wrap multi-line raw UserOperation text in quotes (`"..."`). 
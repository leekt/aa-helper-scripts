import json
import sha3
from eth_abi import encode

# Use relative import for shared utility
# from utils import hex_to_bytes 
from .utils import hex_to_bytes 

def keccak(data_bytes: bytes) -> bytes:
    """Calculates the Keccak-256 hash of the given bytes."""
    hasher = sha3.keccak_256()
    hasher.update(data_bytes)
    return hasher.digest()

def calculate_user_op_hash(user_op_json: str, entry_point_address: str, chain_id: int) -> str:
    """Calculates the userOpHash according to EIP-4337 EntryPoint logic.
    
    Args:
        user_op_json: The JSON string representation of the PackedUserOperation.
        entry_point_address: The address of the EntryPoint contract.
        chain_id: The chain ID.

    Returns:
        The userOpHash as a '0x'-prefixed hex string.
    """
    try:
        user_op = json.loads(user_op_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid UserOperation JSON provided: {e}")

    # --- Prepare data and calculate intermediate hashes --- 
    try:
        sender = user_op['sender']
        if not (isinstance(sender, str) and sender.startswith('0x')):
             raise ValueError("Sender must be a 0x-prefixed hex string")
        nonce = int(user_op['nonce'])
        pre_verification_gas = int(user_op['preVerificationGas'])
        init_code_bytes = hex_to_bytes(user_op['initCode'])
        call_data_bytes = hex_to_bytes(user_op['callData'])
        paymaster_and_data_bytes = hex_to_bytes(user_op['paymasterAndData'])
        account_gas_limits_bytes = hex_to_bytes(user_op['accountGasLimits'])
        if len(account_gas_limits_bytes) != 32:
            raise ValueError(f"accountGasLimits must be 32 bytes, got {len(account_gas_limits_bytes)}")
        gas_fees_bytes = hex_to_bytes(user_op['gasFees'])
        if len(gas_fees_bytes) != 32:
             raise ValueError(f"gasFees must be 32 bytes, got {len(gas_fees_bytes)}")
        if not (isinstance(entry_point_address, str) and entry_point_address.startswith('0x')):
            raise ValueError("EntryPoint address must be a 0x-prefixed hex string")
    except KeyError as e:
        raise ValueError(f"Missing required key in UserOperation JSON: {e}")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid format in UserOperation JSON or arguments: {e}")

    hash_init_code = keccak(init_code_bytes)
    hash_call_data = keccak(call_data_bytes)
    hash_paymaster_and_data = keccak(paymaster_and_data_bytes)

    # --- ABI Encode and Hash --- 
    packed_user_op_part_for_hash = encode(
        ['address', 'uint256', 'bytes32', 'bytes32', 'bytes32', 'uint256', 'bytes32', 'bytes32'],
        [sender, nonce, hash_init_code, hash_call_data, account_gas_limits_bytes, pre_verification_gas, gas_fees_bytes, hash_paymaster_and_data]
    )
    user_op_partial_hash = keccak(packed_user_op_part_for_hash)
    packed_final_for_hash = encode(
        ['bytes32', 'address', 'uint256'],
        [user_op_partial_hash, entry_point_address, chain_id]
    )
    user_op_hash = keccak(packed_final_for_hash)
    return '0x' + user_op_hash.hex()

# --- EIP-191 Hashing Functions --- 

def eip191_hash_bytes(data_bytes: bytes) -> str:
    """Calculates the EIP-191 hash for the given bytes."""
    if len(data_bytes) != 32:
         print(f"Warning: EIP-191 hashing typically expects 32-byte input for hashes, got {len(data_bytes)}.")
    prefix = b'\x19Ethereum Signed Message:\n' + str(len(data_bytes)).encode('ascii')
    message_to_hash = prefix + data_bytes
    hasher = sha3.keccak_256()
    hasher.update(message_to_hash)
    return '0x' + hasher.hexdigest()

def eip191_hash_message(message: str) -> str:
    """Calculates the EIP-191 hash for a UTF-8 string message."""
    try:
        message_bytes = message.encode('utf-8')
    except AttributeError:
         raise TypeError(f"Input message must be a string, got {type(message)}")
    prefix = b'\x19Ethereum Signed Message:\n' + str(len(message_bytes)).encode('ascii')
    message_to_hash = prefix + message_bytes
    hasher = sha3.keccak_256()
    hasher.update(message_to_hash)
    return '0x' + hasher.hexdigest()

def eip191_hash_hex(hex_data: str) -> str:
    """Calculates the EIP-191 hash for data provided as a hex string."""
    try:
        data_bytes = hex_to_bytes(hex_data)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid hex string for EIP-191 hashing: {e}")
    return eip191_hash_bytes(data_bytes) 
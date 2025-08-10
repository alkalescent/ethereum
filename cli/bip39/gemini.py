from mnemonic import Mnemonic

# Initialize the Mnemonic object for the English wordlist
m = Mnemonic("english")

# --- SPLITTING PROCESS ---

# A standard, VALID 24-word BIP39 test vector seed phrase
seed_master = m.generate(256)  # Generate a valid 24-word mnemonic

print("--- Splitting Master Seed ---")
print(f"Original 24-word Master Seed:\n{seed_master}\n")

# Convert the valid 24-word seed to its 256-bit (32-byte) entropy
entropy_master = m.to_entropy(seed_master)
print(f"Master Entropy (32 bytes total):\n{entropy_master.hex()}\n")

# Split the 32-byte entropy into two 16-byte (128-bit) halves
entropy_part_1 = entropy_master[:16]  # First 128 bits
entropy_part_2 = entropy_master[16:]  # Second 128 bits

print(f"Entropy Part 1 (First 16 bytes):\n{entropy_part_1.hex()}")
print(f"Entropy Part 2 (Second 16 bytes):\n{entropy_part_2.hex()}\n")

# Convert each 128-bit entropy half into a new, valid 12-word seed phrase
# Each new phrase will have its own correct 4-bit checksum.
seed_part_1 = m.to_mnemonic(entropy_part_1)
seed_part_2 = m.to_mnemonic(entropy_part_2)

print("--- Generated 12-Word Components ---")
print(f"SEED PART 1: {seed_part_1}")
print(f"SEED PART 2: {seed_part_2}")

print("\n" + "="*50 + "\n")

# --- RECOVERY PROCESS ---

print("--- Recovering Master Seed ---")
print("Using the two 12-word components to reconstruct the original seed.\n")

# Convert the two 12-word parts back to their respective 128-bit entropies
recovered_entropy_1 = m.to_entropy(seed_part_1)
recovered_entropy_2 = m.to_entropy(seed_part_2)

print(f"Recovered Entropy 1:\n{recovered_entropy_1.hex()}")
print(f"Recovered Entropy 2:\n{recovered_entropy_2.hex()}\n")

# Concatenate (join) the two entropy halves to get the original 256 bits
reconstructed_master_entropy = recovered_entropy_1 + recovered_entropy_2
print(f"Reconstructed Master Entropy:\n{reconstructed_master_entropy.hex()}\n")

# Convert the full 256-bit entropy back to the master seed phrase
reconstructed_master_seed = m.to_mnemonic(reconstructed_master_entropy)

print("--- Verification ---")
print(f"Reconstructed 24-word Master Seed:\n{reconstructed_master_seed}\n")

# Verify that the reconstructed seed matches the original
if reconstructed_master_seed == seed_master:
    print("✅ Success! The reconstructed seed matches the original master seed.")
else:
    print("❌ Error! The reconstructed seed does not match the original.")

import streamlit as st

# Fixed simple RSA keys for Alice and Bob

alice_keys = {
    'p': 11,
    'q': 7,
    'n': 77,   # 11 * 7
    'phi': 60, # (11 -1) * (7 -1)
    'e': 7,
    'd': 43    # d such that (d*e) mod 60 = 1
}

bob_keys = {
    'p': 13,
    'q': 5,
    'n': 65,   # 13 * 5
    'phi': 48, # (13 -1) * (5 -1)
    'e': 5,
    'd': 29    # d such that (d*e) mod 48 = 1
}

# Simple letter <-> number mapping for uppercase letters A-Z (A=0 ... Z=25)
def char_to_num(c):
    c = c.upper()
    if 'A' <= c <= 'Z':
        return ord(c) - ord('A')
    else:
        return None  # unsupported character

def num_to_char(n):
    if 0 <= n <= 25:
        return chr(n + ord('A'))
    else:
        return '?'  # out of range

# Modular exponentiation simple display
def mod_exp_simple(base, exponent, modulus):
    result = pow(base, exponent, modulus)
    # Return result and a simple step string
    step_str = f"({base}^{exponent}) mod {modulus} = {result}"
    return result, step_str

# Initialize chat log in session state
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []

st.title("🔐 Simple RSA Chat Demo with Step-by-Step Encryption/Decryption")

st.markdown("""
This demo uses **small RSA keys** fixed for Alice and Bob with a simple mapping of letters to numbers (A=0, B=1, ...).
Each message character is encrypted and decrypted step-by-step showing:

- Letter → number
- Encryption calculation: (number^e) mod n
- Decryption calculation: (encrypted^d) mod n
- Number → letter (decrypted back)
""")

st.markdown("### RSA Keys in use")

st.markdown(f"Alice's public key: (n={alice_keys['n']}, e={alice_keys['e']})")
st.markdown(f"Alice's private key: (n={alice_keys['n']}, d={alice_keys['d']})")

st.markdown(f"Bob's public key: (n={bob_keys['n']}, e={bob_keys['e']})")
st.markdown(f"Bob's private key: (n={bob_keys['n']}, d={bob_keys['d']})")

st.markdown("---")

# Chat interface columns
col_alice, col_bob = st.columns(2)

with col_alice:
    st.subheader("Alice ➡️ Bob")
    alice_input = st.text_input("Enter message from Alice to Bob:", key="alice_text")
    if st.button("Send from Alice"):
        if alice_input:
            cipher_list = []
            steps_enc = []
            steps_dec = []
            decrypted_nums = []
            decrypted_chars = []

            # Prepare message (filter valid characters)
            msg_chars = [c for c in alice_input.upper() if 'A' <= c <= 'Z']
            msg_nums = [char_to_num(c) for c in msg_chars]

            # Encrypt each character using Bob's public key (n,e)
            for idx, num in enumerate(msg_nums, 1):
                ciph, enc_step = mod_exp_simple(num, bob_keys['e'], bob_keys['n'])
                cipher_list.append(ciph)
                steps_enc.append((idx, num_to_char(num), num, enc_step))

            # Decrypt each ciphertext char using Bob's private key (n,d)
            for idx, ciph_num in enumerate(cipher_list, 1):
                dec_num, dec_step = mod_exp_simple(ciph_num, bob_keys['d'], bob_keys['n'])
                decrypted_nums.append(dec_num)
                decrypted_chars.append(num_to_char(dec_num))
                steps_dec.append((idx, ciph_num, dec_num, dec_step))

            # Append to chat log
            st.session_state.chat_log.append({
                'from': 'Alice',
                'to': 'Bob',
                'plaintext': alice_input,
                'filtered_plaintext': ''.join(msg_chars),
                'plain_nums': msg_nums,
                'cipher_list': cipher_list,
                'decrypted_nums': decrypted_nums,
                'decrypted_text': ''.join(decrypted_chars),
                'steps_enc': steps_enc,
                'steps_dec': steps_dec
            })

with col_bob:
    st.subheader("Bob ➡️ Alice")
    bob_input = st.text_input("Enter message from Bob to Alice:", key="bob_text")
    if st.button("Send from Bob"):
        if bob_input:
            cipher_list = []
            steps_enc = []
            steps_dec = []
            decrypted_nums = []
            decrypted_chars = []

            msg_chars = [c for c in bob_input.upper() if 'A' <= c <= 'Z']
            msg_nums = [char_to_num(c) for c in msg_chars]

            # Encrypt with Alice's public key
            for idx, num in enumerate(msg_nums, 1):
                ciph, enc_step = mod_exp_simple(num, alice_keys['e'], alice_keys['n'])
                cipher_list.append(ciph)
                steps_enc.append((idx, num_to_char(num), num, enc_step))

            # Decrypt with Alice's private key
            for idx, ciph_num in enumerate(cipher_list, 1):
                dec_num, dec_step = mod_exp_simple(ciph_num, alice_keys['d'], alice_keys['n'])
                decrypted_nums.append(dec_num)
                decrypted_chars.append(num_to_char(dec_num))
                steps_dec.append((idx, ciph_num, dec_num, dec_step))

            st.session_state.chat_log.append({
                'from': 'Bob',
                'to': 'Alice',
                'plaintext': bob_input,
                'filtered_plaintext': ''.join(msg_chars),
                'plain_nums': msg_nums,
                'cipher_list': cipher_list,
                'decrypted_nums': decrypted_nums,
                'decrypted_text': ''.join(decrypted_chars),
                'steps_enc': steps_enc,
                'steps_dec': steps_dec
            })

st.markdown("---")

st.subheader("📜 Chat History")

if not st.session_state.chat_log:
    st.info("No messages sent yet!")
else:
    for i, msg in enumerate(st.session_state.chat_log, 1):
        st.markdown(f"### Message {i}: {msg['from']} ➡️ {msg['to']}")
        st.markdown(f"**Original message:** {msg['plaintext']}")
        if msg['filtered_plaintext'] != msg['plaintext'].upper():
            st.markdown(f"*Filtered uppercase letters:* {msg['filtered_plaintext']} (only letters A-Z are encrypted)")
        st.markdown(f"**Letters mapped to numbers:** {msg['plain_nums']}")

        st.markdown("#### Encryption Steps:")
        for idx, char, num, step in msg['steps_enc']:
            st.markdown(f"- Char {idx}: '{char}' ({num}) → {step}")

        st.markdown(f"**Ciphertext numbers:** {msg['cipher_list']}")

        st.markdown("#### Decryption Steps:")
        for idx, ciph, dec_num, step in msg['steps_dec']:
            st.markdown(f"- Char {idx}: ciphertext {ciph} → {step} → decrypted number: {dec_num}")

        st.markdown(f"**Decrypted numbers mapped to letters:** {msg['decrypted_nums']}")
        st.markdown(f"**Decrypted text:** {msg['decrypted_text']}")

        if msg['decrypted_text'] == msg['filtered_plaintext']:
            st.success("Decryption successful! Original message recovered.")
        else:
            st.error("Decryption failed! Message mismatch.")

        st.markdown("---")

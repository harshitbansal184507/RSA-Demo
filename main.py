import streamlit as st
import random


def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y

def mod_inverse(e, phi):
    gcd, x, _ = extended_gcd(e, phi)
    if gcd != 1:
        return None
    else:
        return x % phi

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def get_random_prime(start=5, end=50):
    primes = [p for p in range(start, end) if is_prime(p)]
    return random.choice(primes)

def generate_keys():
    p = get_random_prime()
    q = get_random_prime()
    while q == p:
        q = get_random_prime()

    n = p * q
    phi = (p - 1) * (q - 1)

    e = random.choice([x for x in range(3, phi, 2) if extended_gcd(x, phi)[0] == 1])
    d = mod_inverse(e, phi)

    return {
        'p': p,
        'q': q,
        'n': n,
        'phi': phi,
        'e': e,
        'd': d
    }

def char_to_num(c): 
    c = c.upper()
    if 'A' <= c <= 'Z':
        return ord(c) - ord('A')
    else:
        return None

def num_to_char(n):
    if 0 <= n <= 25:
        return chr(n + ord('A'))
    else:
        return '?'

def mod_exp_simple(base, exponent, modulus):
    result = pow(base, exponent, modulus)
    step_str = f"({base}^{exponent}) mod {modulus} = {result}"
    return result, step_str

st.title("🔐 Simple RSA Chat Demo with Step-by-Step Encryption/Decryption (Dynamic Keys)")

if 'alice_keys' not in st.session_state:
    st.session_state.alice_keys = generate_keys()
if 'bob_keys' not in st.session_state:
    st.session_state.bob_keys = generate_keys()

alice_keys = st.session_state.alice_keys
bob_keys = st.session_state.bob_keys

st.subheader("RSA Keys in Use")
st.write(f"Alice's public key: (n={alice_keys['n']}, e={alice_keys['e']})")
st.write(f"Alice's private key: (n={alice_keys['n']}, d={alice_keys['d']})")
st.write(f"Bob's public key: (n={bob_keys['n']}, e={bob_keys['e']})")
st.write(f"Bob's private key: (n={bob_keys['n']}, d={bob_keys['d']})")

# Chat log
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []

col_alice, col_bob = st.columns(2)

# Alice → Bob
with col_alice:
    st.subheader("Alice ➡️ Bob")
    alice_input = st.text_input("Enter message from Alice to Bob:", key="alice_text")
    if st.button("Send from Alice"):
        if alice_input:
            cipher_list, steps_enc, steps_dec = [], [], []
            decrypted_nums, decrypted_chars = [], []

            msg_chars = [c for c in alice_input.upper() if 'A' <= c <= 'Z']
            msg_nums = [char_to_num(c) for c in msg_chars]

            # Encrypt with Bob's public key
            for idx, num in enumerate(msg_nums, 1):
                ciph, enc_step = mod_exp_simple(num, bob_keys['e'], bob_keys['n'])
                cipher_list.append(ciph)
                steps_enc.append((idx, num_to_char(num), num, enc_step))

            # Decrypt with Bob's private key
            for idx, ciph_num in enumerate(cipher_list, 1):
                dec_num, dec_step = mod_exp_simple(ciph_num, bob_keys['d'], bob_keys['n'])
                decrypted_nums.append(dec_num)
                decrypted_chars.append(num_to_char(dec_num))
                steps_dec.append((idx, ciph_num, dec_num, dec_step))

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

# Bob → Alice
with col_bob:
    st.subheader("Bob ➡️ Alice")
    bob_input = st.text_input("Enter message from Bob to Alice:", key="bob_text")
    if st.button("Send from Bob"):
        if bob_input:
            cipher_list, steps_enc, steps_dec = [], [], []
            decrypted_nums, decrypted_chars = [], []

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

# Chat History
st.subheader("📜 Chat History")
if not st.session_state.chat_log:
    st.info("No messages sent yet!")
else:
    for i, msg in enumerate(st.session_state.chat_log, 1):
        st.markdown(f"### Message {i}: {msg['from']} ➡️ {msg['to']}")
        st.markdown(f"**Original message:** {msg['plaintext']}")
        if msg['filtered_plaintext'] != msg['plaintext'].upper():
            st.markdown(f"*Filtered uppercase letters:* {msg['filtered_plaintext']}")
        st.markdown(f"**Letters mapped to numbers:** {msg['plain_nums']}")

        st.markdown("#### Encryption Steps:")
        for idx, char, num, step in msg['steps_enc']:
            st.markdown(f"- Char {idx}: '{char}' ({num}) → {step}")

        st.markdown(f"**Ciphertext numbers:** {msg['cipher_list']}")

        st.markdown("#### Decryption Steps:")
        for idx, ciph, dec_num, step in msg['steps_dec']:
            st.markdown(f"- Char {idx}: ciphertext {ciph} → {step} → decrypted number: {dec_num}")

        st.markdown(f"**Decrypted numbers → letters:** {msg['decrypted_nums']}")
        st.markdown(f"**Decrypted text:** {msg['decrypted_text']}")

        if msg['decrypted_text'] == msg['filtered_plaintext']:
            st.success("Decryption successful!")
        else:
            st.error("Decryption failed!")

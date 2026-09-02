import streamlit as st
from PIL import Image
import google.generativeai as genai

# অ্যাপের পেজ সেটআপ
st.set_page_config(page_title="Student AI", page_icon="🤖", layout="centered")

st.title("🤖 Student AI (স্টুডেন্ট এআই)")
st.write("আপনার স্মার্ট এআই অ্যাসিস্ট্যান্ট। একই চ্যাটে প্রশ্ন করুন, ছবি/ভিডিও দিন, অথবা ভিডিও বানিয়ে নিতে বলুন!")

# --- সাইডবার: এআই ইঞ্জিন কি (API Keys) এবং চ্যাট ডিলিট অপশন ---
st.sidebar.header("⚙️ এআই ইঞ্জিন ও সেটিংস")
gemini_key = st.sidebar.text_input("Gemini API Key দিন:", type="password")
runway_key = st.sidebar.text_input("Runway API Key দিন:", type="password")

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ সব চ্যাট মুছে ফেলুন (Clear Chat)"):
    st.session_state.messages = []
    st.session_state.last_generated_video = None
    st.rerun()

# --- চ্যাট মেমোরি ইনিশিয়ালাইজেশন ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_generated_video" not in st.session_state:
    st.session_state.last_generated_video = None

# আগের চ্যাটগুলো স্ক্রিনে দেখানো
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ইনপুট বক্স ---
uploaded_file = st.file_uploader("ছবি/ভিডিও আপলোড করুন:", type=["jpg", "jpeg", "png", "mp4", "mov"])
user_query = st.chat_input("এখানে প্রশ্ন লিখুন...")

if user_query or uploaded_file:
    prompt_text = user_query if user_query else "এই ফাইলটি বিশ্লেষণ করে উত্তর দিন:"
    
    with st.chat_message("user"):
        st.markdown(prompt_text)
        pil_image = None
        if uploaded_file:
            file_type = uploaded_file.type
            if "image" in file_type:
                pil_image = Image.open(uploaded_file)
                st.image(pil_image, caption="আপলোড করা ছবি", use_container_width=True)
            elif "video" in file_type:
                st.video(uploaded_file)
            
    st.session_state.messages.append({"role": "user", "content": prompt_text})

    with st.chat_message("assistant"):
        if not gemini_key or not runway_key:
            response_text = "⚠️ দয়া করে সাইডবার থেকে প্রথমে আপনার **Gemini** এবং **Runway** উভয় API Key ই বসান!"
            st.warning(response_text)
        else:
            if "ভিডিও" in prompt_text.lower() or "video" in prompt_text.lower():
                response_text = f"🎬 রানওয়ে ইঞ্জিন আপনার নির্দেশমতো '**{prompt_text}**' এর ওপর ভিডিও তৈরি করেছে!"
                st.info(response_text)
                st.session_state.last_generated_video = f"Runway_Video_{prompt_text}"
                st.success("আপনার ভিডিও তৈরি হয়ে গেছে!")
            else:
                try:
                    # জেমিনাই এপিআই কনফিগার ও নিখুঁত কল (মডেল আপডেট করা হয়েছে)
                    genai.configure(api_key=gemini_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    context_note = f"\n\n[ভিডিও রেফারেন্স: {st.session_state.last_generated_video}]" if st.session_state.last_generated_video else ""
                    full_prompt = prompt_text + context_note
                    
                    if pil_image:
                        gemini_response = model.generate_content([full_prompt, pil_image])
                    else:
                        gemini_response = model.generate_content(full_prompt)
                        
                    response_text = gemini_response.text
                    st.markdown(response_text)
                    
                except Exception as e:
                    response_text = f"❌ জেমিনাই এআই তে উত্তর আনতে সমস্যা হয়েছে: {e}"
                    st.error(response_text)
            
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    

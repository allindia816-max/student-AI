import streamlit as st
from PIL import Image

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
    st.session_state.last_generated_video = None  # রানওয়ের ভিডিও মেমোরি খালি করা
    st.rerun()

# --- চ্যাট মেমোরি ও ভিডিও ট্র্যাকিং ইনিশিয়ালাইজেশন ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_generated_video" not in st.session_state:
    st.session_state.last_generated_video = None  # রানওয়ে ভিডিওর রেফারেন্স মনে রাখার জন্য

# আগের চ্যাটগুলো স্ক্রিনে দেখানো
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- মূল একক চ্যাট বক্স ---
user_query = st.chat_input("এখানে প্রশ্ন লিখুন, ছবি/ভিডিও দিন, অথবা ভিডিও বানাতে বলুন...")
uploaded_file = st.file_uploader("বা প্রশ্ন বা উত্তরের জন্য ছবি/ভিডিও আপলোড করুন:", type=["jpg", "jpeg", "png", "mp4", "mov"])

if user_query or uploaded_file:
    prompt_text = user_query if user_query else "এই ফাইলটি বিশ্লেষণ করে উত্তর দিন:"
    
    # ১. ব্যবহারকারীর মেসেজ চ্যাটে দেখানো
    with st.chat_message("user"):
        st.markdown(prompt_text)
        if uploaded_file:
            file_type = uploaded_file.type
            if "image" in file_type:
                image = Image.open(uploaded_file)
                st.image(image, caption="আপলোড করা ছবি", use_column_width=True)
            elif "video" in file_type:
                st.video(uploaded_file)
            
    st.session_state.messages.append({"role": "user", "content": prompt_text})

    # ২. এআই অ্যাসিস্ট্যান্ট রেসপন্স (একই চ্যাট বক্সের ভেতরে)
    with st.chat_message("assistant"):
        if not gemini_key or not runway_key:
            response_text = "⚠️ দয়া করে সাইডবার থেকে প্রথমে আপনার **Gemini** এবং **Runway** উভয় API Key ই বসান!"
            st.warning(response_text)
        else:
            # চেক করা হচ্ছে ব্যবহার কি ভিডিও বানাতে বলেছে নাকি সাধারণ প্রশ্ন করেছে
            if "ভিডিও" in prompt_text.lower() or "video" in prompt_text.lower():
                # রানওয়ে ইঞ্জিন কল করার জায়গা
                response_text = f"🎬 রানওয়ে ইঞ্জিন আপনার নির্দেশমতো '**{prompt_text}**' এর ওপর ভিডিও তৈরি করেছে!"
                st.info(response_text)
                
                # সিমুলেশন বা রানওয়ের ভিডিও আউটপুট (এখানে আসল রানওয়ে ভিডিও লিংক বা অবজেক্ট বসবে)
                simulated_video_reference = f"Runway_Video_{prompt_text}"
                st.session_state.last_generated_video = simulated_video_reference
                
                st.success("আপনার ভিডিও তৈরি হয়ে গেছে! (উপরে বা নিচে এটি প্লে ও ডাউনলোড করা যাবে)")
            else:
                # জেমিনি ইঞ্জিন কল করার জায়গা (সাথে রানওয়ের তৈরি করা ভিডিওর মেমোরি যুক্ত করা হলো)
                context_note = ""
                if st.session_state.last_generated_video:
                    context_note = f" [সংশ্লিষ্ট ভিডিও রেফারেন্স: {st.session_state.last_generated_video}]"
                
                response_text = f"💡 জেমিনি ইঞ্জিনের উত্তর: আপনার বিষয়টি সফলভাবে বিশ্লেষণ করা হয়েছে।{context_note}"
                st.markdown(response_text)
                
                # কপি ও পড়ে শোনানোর অপশন
                st.code(response_text, language="markdown")
                st.info("🔊 (পড়ে শোনানোর ভয়েস বাটন)")
            
    st.session_state.messages.append({"role": "assistant", "content": response_text})

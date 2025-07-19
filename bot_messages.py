"""
Bot messages and interface texts
"""

def get_welcome_message() -> str:
    """Welcome message before user starts the bot"""
    return """
🤖 **Welcome to the Multifunctional AI Bot!**

🚀 **The most complete AI bot on Telegram!**

Access **ALL** major AIs in one place:
• 🧠 **GPT-4o & GPT-4** - Smart chat
• 🎨 **FLUX Pro & Dev** - Image generation
• 🎬 **Luma & MiniMax** - Video creation  
• 🎵 **Suno AI** - Music generation
• 🤖 **Claude 3.5** - Advanced assistant

💰 **Fair and transparent pricing**
🔒 **Secure payment via Stripe**
⚡ **Instant responses**
🌍 **Available 24/7**

👆 **Click /start to begin!**
    """

def get_start_message(user_name: str, plan_name: str) -> str:
    """Start command message"""
    return f"""
🎉 **Hello {user_name}! Welcome to AI Bot!** 

🤖 **Your complete AI assistant is ready!**

**📋 Your current plan:** {plan_name}

**🎯 What I can do for you:**

🧠 **Smart Chat**
• GPT-4o - Advanced conversations
• GPT-4 - Deep analysis  
• Claude 3.5 - Specialized assistant

🎨 **Image Generation**
• FLUX Schnell - Fast and efficient
• FLUX Dev - High quality
• FLUX Pro - Professional quality

🎬 **Video Creation**
• Luma Dream Machine - Realistic videos
• MiniMax Video - Creative animations

🎵 **Music Generation**
• Suno AI - Custom music
• Bark - Sound effects

**⚡ Quick Commands:**
/help - 📖 Complete guide
/plans - 💰 View plans and pricing
/status - 📊 Your current usage
/upgrade - ⬆️ Upgrade plan

**🎯 How to use:**
• Type any question for chat
• `/image <description>` to generate images
• `/video <description>` to create videos
• `/music <description>` to generate music

**🚀 Start right now!** Type your first question or command!
    """

def get_help_message() -> str:
    """Help command message"""
    return """
📖 **Complete AI Bot Guide**

**🎯 MAIN COMMANDS**

💬 **AI Chat**
• Type any question
• Example: "Explain how AI works"

🎨 **Image Generation**
• `/image <description>`
• Example: `/image an astronaut cat in space`

🎬 **Video Creation**
• `/video <description>`
• Example: `/video bird flying over mountains`

🎵 **Music Generation**
• `/music <description>`
• Example: `/music relaxing piano music`

**📊 INFORMATION COMMANDS**

• `/status` - View your current usage
• `/plans` - Plans and pricing
• `/upgrade` - Upgrade your plan
• `/help` - This message

**💡 IMPORTANT TIPS**

✅ **For better results:**
• Be specific in descriptions
• Use visual details for images
• Describe the desired musical style

⏱️ **Processing times:**
• Images: 10-30 seconds
• Videos: 1-3 minutes
• Music: 30-60 seconds
• Chat: Instant

🔄 **Usage limits:**
• Each plan has daily/monthly limits
• Use `/status` to check

**❓ Need help?**
Contact us!
    """

def get_plans_message() -> str:
    """Plans and pricing message"""
    return """
💰 **Plans & Pricing - Choose What's Perfect for You!**

🆓 **FREE - $0/month**
• 5 GPT-4o messages/day
• 3 images/month (FLUX Schnell)
• 1 music/month
• ❌ No videos
• ❌ No GPT-4/Claude

🚀 **STARTER - $9.99/month**
• 50 GPT-4o messages/day
• 15 images/month (FLUX Schnell)
• 3 music/month
• ❌ No videos
• ❌ No GPT-4/Claude

💼 **PRO - $19.99/month** ⭐ *Most Popular*
• 100 GPT-4o messages/day
• 50 images/month (FLUX Dev)
• 10 music/month
• 5 videos/month
• ❌ No GPT-4/Claude

⭐ **PREMIUM - $59.99/month**
• 50 GPT-4o messages/day
• 100 GPT-4 messages/day
• 100 images/month (FLUX Pro)
• 20 music/month
• 10 videos/month
• ❌ No Claude

👑 **ULTIMATE - $149.99/month**
• 100 GPT-4o messages/day
• 200 GPT-4 messages/day
• 200 images/month (FLUX Pro)
• 30 music/month
• 20 videos/month
• 1M Claude tokens/month

**💳 Secure Payment via Stripe**
**🔄 Cancel anytime**
**💰 Prices in USD**

👆 **Use /upgrade to upgrade!**
    """

def get_status_message(user_stats: dict) -> str:
    """User status message"""
    plan_emojis = {
        "FREE": "🆓",
        "STARTER": "🚀", 
        "PRO": "💼",
        "PREMIUM": "⭐",
        "ULTIMATE": "👑"
    }
    
    plan_emoji = plan_emojis.get(user_stats['plan'], "🤖")
    
    return f"""
📊 **Your Current Status**

👤 **User:** {user_stats.get('username', 'N/A')}
{plan_emoji} **Plan:** {user_stats['plan']}

**📈 DAILY USAGE**
🧠 GPT-4o: {user_stats['daily_gpt4o_messages']}/{user_stats['daily_gpt4o_limit']}
🤖 GPT-4: {user_stats['daily_gpt4_messages']}/{user_stats['daily_gpt4_limit']}

**📊 MONTHLY USAGE**
🎨 Images: {user_stats['monthly_images']}/{user_stats['monthly_images_limit']}
🎵 Music: {user_stats['monthly_music']}/{user_stats['monthly_music_limit']}
🎬 Videos: {user_stats['monthly_videos']}/{user_stats['monthly_videos_limit']}
💬 Claude: {user_stats['monthly_claude_tokens']:,}/{user_stats['monthly_claude_limit']:,} tokens

**📅 ACCOUNT INFO**
• Created: {user_stats['created_at']}
• Last activity: {user_stats['updated_at']}

**💡 Tip:** Use `/plans` to see upgrade options!
    """

def get_upgrade_message() -> str:
    """Upgrade message with payment options"""
    return """
⬆️ **Upgrade Your Plan**

🚀 **Unlock the full potential of AI Bot!**

**🎯 Why upgrade?**

✅ More chat messages
✅ More images per month  
✅ Access to videos
✅ Premium models (FLUX Pro)
✅ Access to GPT-4 and Claude
✅ Priority support

**💰 AVAILABLE PLANS:**

🚀 **STARTER - $9.99/month**
• 50 GPT-4o msgs/day
• 15 images/month
• 3 music/month

💼 **PRO - $19.99/month** ⭐
• 100 GPT-4o msgs/day  
• 50 images/month
• 10 music/month
• 5 videos/month

⭐ **PREMIUM - $59.99/month**
• GPT-4o + GPT-4
• 100 images/month (FLUX Pro)
• 20 music/month
• 10 videos/month

👑 **ULTIMATE - $149.99/month**
• Everything from Premium +
• 200 GPT-4 msgs/day
• 200 images/month
• 30 music/month
• 20 videos/month
• Claude 1M tokens/month

**💳 100% secure payment via Stripe**

👆 **Choose your plan:**
/upgrade_starter - $9.99/month
/upgrade_pro - $19.99/month  
/upgrade_premium - $59.99/month
/upgrade_ultimate - $149.99/month
    """

def get_payment_success_message(plan_name: str) -> str:
    """Payment success message"""
    return f"""
🎉 **Payment Confirmed!**

✅ **Your {plan_name} plan has been activated successfully!**

🚀 **Now you have access to:**
• All features of your new plan
• Increased limits
• Premium models
• Priority support

**🎯 Start using right now!**

Type `/status` to see your new limits or start using commands:
• `/image` to generate images
• `/video` to create videos  
• `/music` to generate music

**Thank you for choosing our AI Bot!** 🤖✨
    """

def get_limit_exceeded_message(limit_type: str, plan_name: str) -> str:
    """Limit exceeded message"""
    limit_messages = {
        "daily_gpt4o": "🚫 **Daily GPT-4o limit reached!**",
        "daily_gpt4": "🚫 **Daily GPT-4 limit reached!**",
        "monthly_images": "🚫 **Monthly image limit reached!**",
        "monthly_music": "🚫 **Monthly music limit reached!**",
        "monthly_videos": "🚫 **Monthly video limit reached!**",
        "monthly_claude": "🚫 **Monthly Claude limit reached!**"
    }
    
    message = limit_messages.get(limit_type, "🚫 **Limit reached!**")
    
    return f"""
{message}

**💡 Solutions:**

⬆️ **Upgrade your plan**
• Current plan: {plan_name}
• Use `/upgrade` to see options

⏰ **Wait for renewal**
• Daily limits: renew at midnight
• Monthly limits: renew on subscription date

🆓 **Still available resources:**
• Use `/status` to see what you can still use

👆 **Upgrade now:** /upgrade
    """

def get_error_message(error_type: str = "general") -> str:
    """Error messages"""
    error_messages = {
        "api_error": """
❌ **API Error**

A temporary problem occurred with our services.

**🔄 Try again in a few seconds**

If the problem persists:
• Check if you have sufficient credits
• Contact us
        """,
        "invalid_prompt": """
❌ **Invalid Prompt**

Please provide a valid description.

**📝 Examples:**
• `/image a cute cat`
• `/video bird flying`
• `/music relaxing music`
        """,
        "general": """
❌ **Something went wrong**

An unexpected error occurred.

**🔄 Try again**

If the problem persists, contact us.
        """
    }
    
    return error_messages.get(error_type, error_messages["general"])

def get_generating_message(content_type: str) -> str:
    """Generating content messages"""
    messages = {
        "image": "🎨 **Generating your image...** \n\n⏱️ This may take 10-30 seconds",
        "video": "🎬 **Creating your video...** \n\n⏱️ This may take 1-3 minutes",
        "music": "🎵 **Composing your music...** \n\n⏱️ This may take 30-60 seconds"
    }
    
    return messages.get(content_type, "⏳ **Processing...**")

def get_content_ready_message(content_type: str, prompt: str, cost: float, model: str) -> str:
    """Content ready messages"""
    type_emojis = {
        "image": "🎨",
        "video": "🎬", 
        "music": "🎵"
    }
    
    emoji = type_emojis.get(content_type, "✅")
    
    return f"""
{emoji} **{content_type.title()} generated successfully!**

**📝 Prompt:** {prompt}
**🤖 Model:** {model}
**💰 Cost:** ${cost:.4f}

**🎯 Like the result?** 
Try other commands or upgrade for more features!
    """


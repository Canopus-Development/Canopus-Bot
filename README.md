
# Canopus Discord Bot

An advanced, feature-rich Discord bot designed for server management, project coordination, and professional team collaboration. Developed by [Gamecooler19 (Pradyumn Tandon)](https://github.com/gamecooler19) and [Canopus Development](https://github.com/canopus-development).


## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Commands](#commands)
  - [Moderation](#moderation)
  - [Administration](#administration)
  - [Utility](#utility)
  - [Project Management](#project-management)
  - [Professional Engagement](#professional-engagement)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

### 🛡️ Moderation
- Kick, ban, mute, and warn members
- Timeout functionality
- Purge messages
- Moderation logs

### ⚙️ Administration
- Create and delete channels
- Manage roles and permissions
- Server information display
- Slowmode control
- Announcement system

### 🔧 Utility
- Create polls
- Set reminders
- User and role information
- Reaction roles
- Welcome messages
- Emoji management

### 📊 Project Management
- Task creation and assignment
- Task listing and updating
- Meeting scheduler with reminders
- Team assignment and management

### 👥 Professional Engagement
- Conduct team standups
- Feedback submission system
- FAQ management
- Resource sharing
- Milestone announcements
- Project linking

## Installation

### Prerequisites

- Python 3.8+
- Discord bot token
- Discord application ID
- Necessary permissions for the bot (administrator recommended)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Canopus-Development/canopus-bot.git
   cd canopus-bot
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Create a `.env` file in the root directory.
     ```env
     BOT_TOKEN=your-discord-bot-token
     APP_ID=your-application-id
     ```
   - Replace `your-discord-bot-token` and `your-application-id` with your actual bot token and application ID.

5. **Run the bot**
   ```bash
   python main.py
   ```

## Configuration

### Environment Variables

- **Required**
  - `BOT_TOKEN`: Your Discord bot token
  - `APP_ID`: Your Discord application ID

- **Optional**
  - Customize settings within the code or extend functionality by modifying the cog files.

## Usage

Invite the bot to your server using the OAuth2 URL with the necessary scopes and permissions.

## Commands

### Moderation

| Command          | Description                         | Permission              |
|------------------|-------------------------------------|-------------------------|
| `/kick`          | Kick a member                       | Kick Members            |
| `/ban`           | Ban a member                        | Ban Members             |
| `/timeout`       | Timeout a member                    | Moderate Members        |
| `/warn`          | Warn a member                       | Moderate Members        |
| `/mute`          | Mute a member                       | Moderate Members        |
| `/unmute`        | Unmute a member                     | Moderate Members        |
| `/lockchannel`   | Lock a channel                      | Manage Channels         |
| `/unlockchannel` | Unlock a channel                    | Manage Channels         |
| `/modlog`        | View moderation logs                | View Audit Log          |

### Administration

| Command         | Description                      | Permission         |
|-----------------|----------------------------------|--------------------|
| `/createchannel`| Create a new text channel        | Manage Channels    |
| `/deletechannel`| Delete a channel                 | Manage Channels    |
| `/createrole`   | Create a new role                | Manage Roles       |
| `/deleterole`   | Delete a role                    | Manage Roles       |
| `/serverinfo`   | Display server information       | Administrator      |
| `/slowmode`     | Set slowmode for a channel       | Manage Channels    |
| `/announce`     | Make an announcement             | Administrator      |
| `/setnickname`  | Change a member's nickname       | Manage Nicknames   |
| `/permissions`  | Manage channel permissions       | Manage Roles       |

### Utility

| Command         | Description                      | Permission             |
|-----------------|----------------------------------|------------------------|
| `/poll`         | Create a poll                    | —                      |
| `/remindme`     | Set a personal reminder          | —                      |
| `/userinfo`     | Display user information         | —                      |
| `/roleinfo`     | Display role information         | —                      |
| `/pinmessage`   | Pin a message in the channel     | Manage Messages        |
| `/reactionrole` | Create a reaction role message   | Manage Roles           |
| `/setwelcome`   | Set up welcome messages          | Administrator          |
| `/testwelcome`  | Test the welcome message         | Administrator          |

### Project Management

| Command         | Description                      | Permission             |
|-----------------|----------------------------------|------------------------|
| `/taskcreate`   | Create a new task                | —                      |
| `/taskupdate`   | Update a task's status           | —                      |
| `/tasklist`     | List all tasks                   | —                      |
| `/taskdelete`   | Delete a task                    | —                      |
| `/meeting`      | Schedule a meeting               | —                      |
| `/teamassign`   | Assign a member to a team        | —                      |
| `/teamremove`   | Remove a member from a team      | —                      |
| `/teamlist`     | List team members                | —                      |

### Professional Engagement

| Command         | Description                      | Permission             |
|-----------------|----------------------------------|------------------------|
| `/standup`      | Conduct a team standup           | —                      |
| `/standupreport`| Generate a standup report        | —                      |
| `/faq`          | Manage FAQ entries               | Manage Messages        |
| `/feedback`     | Submit feedback                  | —                      |
| `/resources`    | Access learning resources        | —                      |
| `/milestone`    | Announce a project milestone     | Manage Messages        |
| `/teaminfo`     | Display team/project information | —                      |
| `/linkproject`  | Link project resources           | —                      |

## Project Structure

```
canopus-bot/
├── main.py
├── cogs/
│   ├── moderation.py
│   ├── admin.py
│   ├── utility.py
│   ├── project_management.py
│   ├── professional.py
│   ├── welcome.py
├── events/
│   └── on_message.py
├── data/
│   ├── tasks.json
│   ├── faq.json
│   ├── resources.json
├── assets/
│   └── banner.png
├── requirements.txt
├── README.md
└── LICENSE
```

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit your changes**
   ```bash
   git commit -m "Add YourFeature"
   ```

4. **Push to your branch**
   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

## Support

- **Discord Server:** [Join us on Discord](https://discord.gg/your-invite)
- **Issues:** [Report bugs or request features](https://github.com/gamecooler19/canopus-bot/issues)
- **Email:** support@canopusdevelopment.com

## License

This project is licensed under the **[Canopus Development License](LICENSE)**.

## Acknowledgments

- **[discord.py](https://github.com/Rapptz/discord.py):** Python library for Discord API
- **Contributors:** Thanks to all the contributors who have helped improve this project.
- **Community:** Thank you to the Discord community for your support and feedback.

---

*Developed by [Gamecooler19 (Pradyumn Tandon)](https://github.com/gamecooler19) and [Canopus Development](https://github.com/canopus-development).*

---
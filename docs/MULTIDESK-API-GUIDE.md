# MultiDesk — Staff guide: how to use

Use this guide to log in, connect to another computer, and use the address book. **You do not need to change any server settings**; MultiDesk is already configured for our systems.

---

## 1. Log in (first time or new device)

1. Open **MultiDesk**.
2. Click the **Settings** (gear) icon, or the **⋮** menu next to your ID and choose **Settings**.
3. Open the **Account** tab.
4. Click **Login**.
5. Enter the **username** and **password** you were given (e.g. by IT).
6. Click **Login** / **OK**.

When you see your username in the Account section, you are logged in. Your **address book** will then sync so you can see shared contacts and your saved computers.

---

## 2. Your ID — so others can connect to you

- On the main screen, your **ID** is the number under “Your Desktop” (e.g. `912 345 678`).
- **Give this ID** (and the one-time password if it’s shown) to a colleague when they need to connect to your computer.
- You can **copy your ID** by clicking the **⋮** next to it and choosing **Copy ID**, or by double‑clicking the ID.

---

## 3. Connecting to another computer

### By ID (when someone gave you their ID)

1. In the **Remote ID** box, type (or paste) the other person’s ID.
2. If they gave you a **password**, enter it when prompted.
3. Click **Connect** (or **Remote control** / **File transfer** if you see those options).

### From the Address Book (recommended)

1. Open the **Address Book** tab (next to Recent, Favorites, etc.).
2. Find the person or computer you want (use search if the list is long).
3. Click the **Connect** (or monitor) button on that entry, or right‑click and choose **Connect**.
4. Enter the password if asked.

You can also use **Recent** to reconnect to computers you’ve used before, or **Favorites** if you’ve added them.

---

## 4. Using the Address Book

- **Address Book** shows computers/contacts that are set up for your account. It syncs when you’re **logged in**.
- **Connect** — Click the connect/control button on a contact to start a remote session.
- **File transfer** — Use the menu (⋮ or right‑click) on a contact and choose **File transfer** if you only need to send/receive files.
- **Add to Favorites** — From the menu on a contact, choose **Add to Favorites** so they appear in the Favorites tab.
- **Tags and notes** — You can add tags or notes to contacts from the menu to organise the list (e.g. “Support”, “Branch A”).

If the Address Book is empty or shows an error, make sure you are **logged in** (Settings → Account). If it still doesn’t load, contact IT.

---

## 5. During a remote session

- **Full control** — You can use the other computer’s mouse and keyboard as normal.
- **File transfer** — Use the file-transfer option in the session toolbar if you need to copy files.
- **End session** — Close the remote window or use the disconnect/close button in the toolbar.

---

## 6. Logging out

1. Open **Settings** → **Account**.
2. Click **Logout**.

After logout, your address book will no longer sync on this device until you log in again.

---

## 7. Admin portal (rustdesk-api)

Staff who need to manage users or the address-book service can use the **Admin portal** in a web browser.

1. **Open the Admin portal**  
   In your browser go to the address provided by IT. It will look like one of these:
   - `http://<your-server>:21114/_admin/`
   - `https://<your-server>/_admin/`  
   Replace `<your-server>` with the hostname or URL you were given (e.g. `epyc1admin.multisaas.co.za` or your company API URL).

2. **Log in**  
   Use the **admin username and password** you were given. This is often a separate admin account (e.g. username `admin`) and not the same as your MultiDesk login, unless IT has told you otherwise.

3. **What you can do in the portal**  
   - Create or remove user accounts (for staff to log in to MultiDesk).
   - Manage permissions and shared address books.
   - View or manage the service, depending on your role.

If you don't have the Admin portal URL or admin login details, contact IT.

---

## 8. If something doesn’t work

| What happens | What to do |
|--------------|------------|
| **“Failed to connect”** | Check the ID is correct and the other computer has MultiDesk running and is on the network. Ask them for the current one-time password if required. |
| **Address book empty or error** | Confirm you are **logged in** (Settings → Account). If yes, contact IT. |
| **Login fails** | Check username and password (no extra spaces). If you don’t have an account or forgot the password, contact IT. |
| **Can’t find Settings** | Use the **⋮** menu next to your ID and choose **Settings**, or look for the gear icon in the window. |

**For account issues, access problems, or new users:** contact your IT or the person who gave you MultiDesk.

**For Admin portal URL or admin access:** contact IT.

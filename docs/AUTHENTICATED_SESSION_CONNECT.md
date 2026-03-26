# Authenticated Session Connect Override

## Why This Exists

MultiDesk stays very close to upstream RustDesk, but there is one intentional
divergence in [ui_session_interface.rs](/C:/Users/Ken/multidesk/src/ui_session_interface.rs).

When a desktop client is logged into `rustdesk-api`, upstream RustDesk loads the
saved `access_token` into the session connect path. If both `key` and `token`
are present, the client enters the rendezvous `secure_tcp()` handshake before
asking `hbbs` to punch or relay the session.

With `rustdesk-api` plus stock `hbbs` and `hbbr`, that authenticated handshake
times out in our deployment. The observable client error is:

`Failed to secure tcp: deadline has elapsed`

Anonymous connects continue to work because they do not include the token and
therefore skip the authenticated `secure_tcp()` path.

## The Patch

By default, MultiDesk now keeps the saved `access_token` for account and API
features, but does not inject it into session connection setup. This avoids the
failing authenticated rendezvous path while keeping the rest of the login and
address-book functionality intact.

The code change is intentionally narrow:

- only the session connect token lookup is overridden
- the transport code in `client.rs` and `common.rs` remains untouched
- upstream behavior can be restored at runtime

## Runtime Escape Hatch

Set this environment variable to restore upstream authenticated session connect
behavior without changing code:

```text
MULTIDESK_ENABLE_SESSION_ACCESS_TOKEN=1
```

Accepted truthy values are `1`, `true`, `yes`, and `on`.

If the server stack is fixed in the future, this is the quickest way to verify
whether the workaround is still needed before removing the patch.

## When To Remove It

Remove this override only after confirming all of the following:

1. logged-in desktop connects succeed against the target backend
2. the `secure_tcp()` rendezvous handshake completes reliably
3. stock RustDesk and MultiDesk behave the same in the logged-in session path

At that point, the patch can be reverted by:

1. removing `get_session_access_token()`
2. removing `use_authenticated_session_connect()`
3. changing `io_loop()` back to `LocalConfig::get_option("access_token")`

## Why We Chose This Approach

This workaround was chosen because it keeps the divergence from upstream as
small as possible:

- no server protocol changes
- no edits to the core handshake implementation
- no behavior changes for account storage itself
- one well-documented override point with an opt-in switch for upstream behavior

# Step 5: Publish

Your agent builds your dashboard (and public page and CV, if you chose them) from the
spreadsheet, shows them to you, and then puts them online on your own free Cloudflare account.

> **Your agent does:** builds everything on your computer first and shows you. Then it publishes
> the public page, and uploads a **locked** placeholder for the dashboard, with no data in it,
> until the login is on. It guides you through turning the login on, then uploads the real
> dashboard and checks that a stranger only sees a login page.

> **You do:** create a free Cloudflare account (or use yours) and log in once. Turn on the
> login for your dashboard, about 8 clicks with your agent guiding you. Then open both sites on
> your phone.

## The login

Cloudflare calls it **Access**. You choose who may enter, by email address: you, and anyone you
picked. To enter, you type your email and Cloudflare sends you a one-time code. No password to
remember.

The first time, Cloudflare may ask you to set up "Zero Trust" and pick its **Free** plan. It may
ask for a payment card even for the free plan; your agent will tell you before, and you decide.

## Addresses

| Option | Looks like | Cost |
|---|---|---|
| Free address | `maya-crm.yourname.workers.dev` | free |
| A domain you own | `crm.maya.com` | free if you already have it |
| Buy a domain | `mayalindqvist.com` | about 10-15 USD a year, you buy it |

## Check the public page together

Read it line by line with your agent. Your phone number is never on it, not even in the CV you
can download there (only your own copy of the CV has it), but
anything written in your CV lines is public. Nothing about health, money, ID numbers or other
people's private details belongs there.

> **No Cloudflare?** The dashboard also works as a file on your computer: open it in any
> browser, even offline. It just does not update itself.

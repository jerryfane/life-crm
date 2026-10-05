# Step 6: Your assistant

After setup you should not need your agent day to day. Instead, you chat with the AI assistant
you already use (on your phone, for example), and it keeps the spreadsheet current.

> **Your agent does:** writes a guide file for your assistant and puts it in your Drive folder.
> It explains each tab and column of *your* sheet, what the assistant may change on its own,
> what needs your yes first, and the rules: never invent facts, keep private things private.
> Then it tests the assistant with you.

> **You do:** connect your chat assistant to Google Drive (most have a Drive connector in their
> settings) and add one instruction: *"Before answering about my CRM, read GUIDE.md in my Maya
> CRM folder."* Then send two test messages.

## The two tests

```text
What are my next three deadlines?
```

```text
Today I finished the Surgery II assignment.
```

The first should list real dates from your sheet. After the second, the task should be marked
done, and an update row added. Your agent checks the sheet and fixes the guide if the assistant
got it wrong.

## What your assistant may do

| On its own | Only after your yes |
|---|---|
| Mark a step done when you say so | Anything that appears on your public page |
| Add a step with a date you gave | Deleting rows |
| Add an update to the log | New lanes, pages or columns |

Some assistants can read Drive but not edit it. They can still answer questions and suggest
the exact change; you paste it into the sheet.

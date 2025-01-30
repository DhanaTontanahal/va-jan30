import { v4 as uuidv4 } from "uuid"; // Use uuid to generate unique IDs

const transformTransactions = (transactions) => {
  // Check if transactions are empty or null
  if (!transactions || transactions.length === 0) {
    // Generate random data if no transactions are available
    return Array.from({ length: 5 }, (_, index) => ({
      id: `txn${index + 1}`,
      $id: `rec${uuidv4().slice(0, 8)}`,
      name: `Random User ${index + 1}`,
      paymentChannel: "Online",
      type: index % 2 === 0 ? "Debit" : "Credit",
      accountId: `ACC${Math.floor(Math.random() * 1000000)}`,
      amount: (Math.random() * 500).toFixed(2), // Random amount between 0-500
      pending: Math.random() > 0.5,
      category: ["Shopping", "Bills", "Entertainment", "Groceries", "Travel"][
        Math.floor(Math.random() * 5)
      ],
      date: new Date(Date.now() - Math.random() * 10000000000)
        .toISOString()
        .split("T")[0], // Random past date
      image: "https://example.com/images/default.png", // Default placeholder image
      $createdAt: new Date().toISOString(),
      channel: ["Web", "Mobile", "ATM"][Math.floor(Math.random() * 3)],
      senderBankId: `BANK${Math.floor(Math.random() * 1000)}`,
      receiverBankId: `BANK${Math.floor(Math.random() * 1000)}`,
    }));
  }

  // Transform existing transactions to match the required structure
  return transactions.map((t) => ({
    id: `txn${t.transaction_id}`,
    $id: `rec${uuidv4().slice(0, 8)}`,
    name: `User ${t.transaction_id}`,
    paymentChannel: "Online",
    type: t.transaction_type === "Pay Bill" ? "Debit" : "Credit",
    accountId: `ACC123456`,
    amount: t.transaction_amount,
    pending: false,
    category: t.transaction_type,
    date: new Date(t.transaction_datetime).toISOString().split("T")[0],
    image: `https://example.com/images/txn${t.transaction_id}.png`, // Placeholder image for each transaction
    $createdAt: new Date(t.transaction_datetime).toISOString(),
    channel: "Web",
    senderBankId: `BANK${Math.floor(Math.random() * 1000)}`,
    receiverBankId: `BANK${Math.floor(Math.random() * 1000)}`,
  }));
};

export default transformTransactions;

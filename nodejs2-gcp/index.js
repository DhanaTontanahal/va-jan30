const express = require("express");
const cors = require("cors");
const mysql = require("mysql2");
const app = express();
const port = process.env.PORT || 8080;

app.use(cors());
app.use(express.json());

app.get("/", async (req, res) => {
  res.json({ status: "Bark bark jan28 new" });
});
// Endpoint to get account balance based on email
app.get("/api/account-balance", (req, res) => {
  console.log("here");
  const email = req.query.email;

  if (!email) {
    return res.status(400).json({ error: "Email is required" });
  }

  const getUserQuery = "SELECT user_id FROM users WHERE user_email = ?";
  const getBalanceQuery =
    "SELECT account_number, balance FROM account_balance WHERE user_id = ?";

  // Fetch user ID based on email
  db.query(getUserQuery, [email], (err, userResults) => {
    if (err) {
      return res.status(500).json({ error: "Database query failed" });
    }

    if (userResults.length === 0) {
      return res.status(404).json({ error: "User not found" });
    }

    const userId = userResults[0].user_id;

    // Fetch account balance based on user ID
    db.query(getBalanceQuery, [userId], (err, balanceResults) => {
      if (err) {
        return res
          .status(500)
          .json({ error: "Failed to fetch account balance" });
      }

      if (balanceResults.length === 0) {
        return res.status(404).json({ error: "Account balance not found" });
      }

      console.log(balanceResults);
      res.json({
        accountNumber: balanceResults[0].account_number,
        balance: balanceResults[0].balance,
      });
    });
  });
});

app.get("/api/recent-transactions", (req, res) => {
  const email = req.query.email; // Get email from query params

  if (!email) {
    return res.status(400).json({ error: "Email is required" });
  }

  const getUserQuery = "SELECT user_id FROM users WHERE user_email = ?";
  const getTransactionsQuery = `
      SELECT transaction_id, transaction_type, transaction_amount, transaction_datetime 
      FROM transactions 
      WHERE user_id = ? 
      ORDER BY transaction_datetime DESC 
      LIMIT 10;
    `;

  // Fetch user ID based on email
  db.query(getUserQuery, [email], (err, userResults) => {
    if (err) {
      return res.status(500).json({ error: "Database query failed" });
    }

    if (userResults.length === 0) {
      return res.status(404).json({ error: "User not found" });
    }

    const userId = userResults[0].user_id;

    // Fetch recent transactions based on user ID
    db.query(getTransactionsQuery, [userId], (err, transactionResults) => {
      if (err) {
        return res.status(500).json({ error: "Failed to fetch transactions" });
      }

      if (transactionResults.length === 0) {
        return res.status(404).json({ error: "No transactions found" });
      }

      console.log(transactionResults);
      res.json(transactionResults);
    });
  });
});

const ELIGIBILITY_CRITERIA = {
  minAge: 18,
  minIncome: 30000,
  allowedNationalities: ["US", "Canada", "India"],
};

const getMainMenuOptions = () => {
  return [
    {
      text: "Total transactions in last month",
    },
    {
      text: "Check eligibility",
    },
    {
      text: "Track application",
    },
    {
      text: "Type any question",
    },
  ];
};
function getApplicationStatus(applicationId) {
  return new Promise((resolve, reject) => {
    const query = `
        SELECT status 
        FROM application_status 
        WHERE application_id = ?;
      `;

    db.query(query, [applicationId], (err, results) => {
      if (err) {
        return reject(err); // Handle query errors
      }

      if (results.length === 0) {
        resolve("Not Found"); // If no results, return "Not Found"
      } else {
        resolve(results[0].status); // Return the status from the database
      }
    });
  });
}

// const db = mysql.createConnection({
//   host: "127.0.0.1",
//   user: "root", // Replace with your DB username
//   password: "yourpassword", // Replace with your DB password
//   database: "menu_logger", // Replace with your DB name
//   port: 3306,
// });

const db = mysql.createConnection({
  host: "127.0.0.1",
  user: "root", // Replace with your DB username
  password: "yourpassword", // Replace with your DB password
  database: "menu_logger", // Replace with your DB name
  port: 3306,
});

// Connect to the database
db.connect((err) => {
  if (err) {
    console.error(
      "Database connection failed---------------------------------------------------------------------------------",
      err.stack
    );
    return;
  }
  console.log("Connected to the database.");
});

// Retrieve the last 5 transactions for a user from the database
function getLastFiveTransactionsFromDB(userId) {
  return new Promise((resolve, reject) => {
    const query = `
        SELECT transaction_type, transaction_amount, transaction_datetime 
        FROM transactions 
        WHERE user_id = ? 
        ORDER BY transaction_datetime DESC 
        LIMIT 5;
      `;

    db.query(query, [userId], (err, results) => {
      if (err) {
        return reject(err);
      }
      resolve(results);
    });
  });
}

// Function to fetch transactions for the last month
function getTransactionsLastMonth(userId) {
  return new Promise((resolve, reject) => {
    const query = `
        SELECT transaction_type, transaction_amount, transaction_datetime
        FROM transactions
        WHERE user_id = ? 
          AND transaction_datetime BETWEEN 
              DATE_SUB(LAST_DAY(CURDATE() - INTERVAL 1 MONTH), INTERVAL DAY(LAST_DAY(CURDATE() - INTERVAL 1 MONTH)) - 1 DAY)
              AND LAST_DAY(CURDATE() - INTERVAL 1 MONTH)
        ORDER BY transaction_datetime;
      `;

    db.query(query, [userId], (err, results) => {
      if (err) {
        return reject(err);
      }
      resolve(results);
    });
  });
}

// Retrieve the account balance for a user
function getAccountBalance(userId) {
  return new Promise((resolve, reject) => {
    const query = `
      SELECT account_number, balance 
      FROM account_balance 
      WHERE user_id = ?;
    `;
    db.query(query, [userId], (err, results) => {
      if (err) {
        return reject(err);
      }
      if (results.length === 0) {
        resolve(null); // No account found
      } else {
        resolve(results[0]); // Return the account details
      }
    });
  });
}

// Function to calculate total payments for the last month
function getPaymentsLastMonth(userId) {
  return new Promise((resolve, reject) => {
    const query = `
        SELECT SUM(payment_amount) AS total_payment
        FROM card_payments
        WHERE user_id = ? 
          AND payment_month BETWEEN 
              DATE_SUB(LAST_DAY(CURDATE() - INTERVAL 1 MONTH), INTERVAL DAY(LAST_DAY(CURDATE() - INTERVAL 1 MONTH)) - 1 DAY)
              AND LAST_DAY(CURDATE() - INTERVAL 1 MONTH);
      `;

    db.query(query, [userId], (err, results) => {
      if (err) {
        return reject(err);
      }
      resolve(results[0]?.total_payment || 0);
    });
  });
}

// Function to fetch the current credit card balance
function getCreditCardBalance(userId) {
  return new Promise((resolve, reject) => {
    const query = `
        SELECT current_balance, credit_limit
        FROM credit_card_balance
        WHERE user_id = ?;
      `;

    db.query(query, [userId], (err, results) => {
      if (err) {
        return reject(err);
      }
      resolve(results[0] || { current_balance: 0, credit_limit: 0 });
    });
  });
}

// Dialogflow webhook endpoint
app.post("/", async (req, res) => {
  try {
    // Access queryResult from the request
    const queryResult = req.body.queryResult;

    // Validate queryResult exists
    if (!queryResult) {
      throw new Error("Missing queryResult in the request body.");
    }

    // Extract intent name
    const intentName = queryResult.intent.displayName;
    console.log("Intent Name:", intentName);

    // Check for specific intent
    if (intentName === "track.application - context:ongoing-tracking") {
      const parameters = queryResult.parameters;
      const applicationId = parameters.applicationId;

      // Validate applicationId
      if (!applicationId) {
        throw new Error("Missing applicationId in parameters.");
      }

      const status = await getApplicationStatus(applicationId);
      console.log("Application Status:", status);

      // Send response back to Dialogflow
      res.json({
        fulfillmentMessages: [
          {
            text: {
              text: [`Your application status is: ${status}.`],
            },
          },
          {
            payload: {
              richContent: [
                [
                  {
                    type: "chips",
                    options: getMainMenuOptions(),
                  },
                ],
              ],
            },
          },
        ],
      });
    } else if (intentName === "transactions.calculate") {
      const userId = req.body.queryResult.parameters.user_id; // Assuming user_id is passed in the request
      // Fetch data
      const [transactions, payments, balance, accountDetails] =
        await Promise.all([
          getTransactionsLastMonth(userId),
          getPaymentsLastMonth(userId),
          getCreditCardBalance(userId),
          getAccountBalance(userId),
        ]);

      // const accountDetails = await getAccountBalance(userId);

      console.log(transactions, payments, balance);
      // Prepare response
      const transactionDetails = transactions
        .map(
          (t) =>
            `${t.transaction_type} of $${t.transaction_amount} on ${t.transaction_datetime}`
        )
        .join("\n");

      const responseText = `
          Transactions Last Month:
          Associated with account Number: ${accountDetails.account_number}\nBalance: $${accountDetails.balance}
          Credit card transactions:
          Total Payment Done Last Month: $${payments}
          Current Credit Card Balance: $${balance?.current_balance} (Limit: $${balance.credit_limit})
        `;

      // Send response
      res.json({
        fulfillmentMessages: [
          {
            text: {
              text: [responseText],
            },
          },
          {
            payload: {
              richContent: [
                [
                  {
                    type: "chips",
                    options: getMainMenuOptions(),
                  },
                ],
              ],
            },
          },
        ],
      });
    } else if (intentName === "last.transactions") {
      const parameters = queryResult.parameters;
      const userId = parseInt(parameters.user_id); // Ensure user_id is an integer

      if (!userId) {
        throw new Error("Missing user_id in parameters.");
      }

      console.log("User ID:", userId);

      // Fetch the last 5 transactions
      //   const lastTransactions = getLastFiveTransactions(userId);
      const lastTransactions = await getLastFiveTransactionsFromDB(userId);

      if (lastTransactions.length === 0) {
        res.json({
          fulfillmentMessages: [
            {
              text: {
                text: ["No recent transactions found."],
              },
            },
            {
              payload: {
                richContent: [
                  [
                    {
                      type: "chips",
                      options: getMainMenuOptions(),
                    },
                  ],
                ],
              },
            },
          ],
        });
        return;
      }

      // Format the response
      const transactionList = lastTransactions
        .map(
          (t) =>
            `${t.transaction_type} of $${t.transaction_amount} on ${t.transaction_datetime}`
        )
        .join("\n");

      res.json({
        fulfillmentMessages: [
          {
            text: {
              text: [`Here are your last 5 transactions:\n${transactionList}`],
            },
          },
          {
            payload: {
              richContent: [
                [
                  {
                    type: "chips",
                    options: getMainMenuOptions(),
                  },
                ],
              ],
            },
          },
        ],
      });
    } else if (
      intentName === "learn.more" ||
      intentName === "return.mainmenu"
    ) {
      res.json({
        fulfillmentMessages: [
          {
            text: {
              text: [`Here are your options`],
            },
          },
          {
            payload: {
              richContent: [
                [
                  {
                    type: "chips",
                    options: getMainMenuOptions(),
                  },
                ],
              ],
            },
          },
        ],
      });
    } else if (intentName === "Default Welcome Intent") {
      console.log(req.body.originalDetectIntentRequest);
      const payload =
        req.body.originalDetectIntentRequest?.payload?.userName || "there";

      console.log("Extracted userName:", payload);

      res.json({
        fulfillmentMessages: [
          {
            text: {
              text: [
                `Hello ${payload}, I’m your Virtual Assistant. How can I help you today? You can ask me about credit cards, application process, eligibility, and more!`,
              ],
            },
          },
          {
            payload: {
              richContent: [
                [
                  {
                    type: "chips",
                    options: getMainMenuOptions(),
                  },
                ],
              ],
            },
          },
        ],
      });
    } else if (intentName === "User Login Intent") {
      // Example: Extract user input (e.g., email and password)
      const parameters = req.body.queryResult.parameters;
      const email = parameters.email || "urwithdhanu@gmail.com";
      const password = parameters.password || "NoPasswordProvided";

      console.log("User Login Details:", { email, password });

      // Perform login logic here (e.g., validate against a database)
      const isAuthenticated = true;

      if (isAuthenticated) {
        res.json({
          fulfillmentMessages: [
            {
              text: {
                text: [
                  `Welcome back, ${email}! You're successfully logged in.`,
                ],
              },
            },
            {
              payload: {
                richContent: [
                  [
                    {
                      type: "chips",
                      options: [
                        {
                          text: "Last Transactions",
                        },
                        {
                          text: "Check eligibility",
                        },
                        {
                          text: "Track application",
                        },
                      ],
                    },
                  ],
                ],
              },
            },
          ],
        });
      } else {
        res.json({
          fulfillmentMessages: [
            {
              text: {
                text: ["Invalid credentials. Please try again."],
              },
            },
          ],
        });
      }
    } else {
      console.log("Unknown intent:", intentName);
      res.status(400).send("Unhandled intent.");
    }
  } catch (error) {
    console.error("Error handling webhook:", error.message);
    res.status(500).send({
      fulfillmentMessages: [
        {
          text: {
            text: [`Error: ${error.message}`],
          },
        },
      ],
    });
  }
});

// Start server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});

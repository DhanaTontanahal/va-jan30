"use client";
import React, { useState, useEffect } from "react";
import axios from "axios";
import transformTransactions from "./transformTransactions"; // Adjust the path
import TransactionsTable from "./TransactionsTable"; // Adjust the path

const RecentTransactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const authUser = JSON.parse(localStorage.getItem("authUser"));

    if (authUser && authUser.email) {
      const email = authUser.email;

      axios
        .get(
          `https://va-nodejs-app2-855220130399.us-central1.run.app//api/recent-transactions?email=urwithdhanu@gmail.com`
        )
        .then((response) => {
          const transformedData = transformTransactions(response.data);
          setTransactions(transformedData);
        })
        .catch((error) => {
          if (error.response) {
            setError(
              error.response.data.error || "Error fetching transactions"
            );
          } else {
            setError("Failed to connect to the server.");
          }

          // Generate random data if there's an error
          const randomData = transformTransactions([]);
          setTransactions(randomData);
        });
    } else {
      setError("User not logged in or email not found.");
    }
  }, []);

  return (
    <div style={{ padding: "5px" }}>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <TransactionsTable transactions={transactions} />
    </div>
  );
};

export default RecentTransactions;

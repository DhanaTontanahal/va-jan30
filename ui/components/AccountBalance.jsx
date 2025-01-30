"use client";
import React, { useState, useEffect } from "react";
import axios from "axios";
import AnimatedCounter from "./AnimatedCounter";
import DoughnutChart from "./DoughnutChart";

const AccountBalance = () => {
  const [accountBalance, setAccountBalance] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    // Get the logged-in user from localStorage
    const authUser = JSON.parse(localStorage.getItem("authUser"));
    console.log(authUser);
    if (authUser && authUser.email) {
      const email = authUser.email;

      console.log(email);
      // Fetch account balance from the backend
      axios
        .get(
          `https://va-nodejs-app-855220130399.us-central1.run.app/api/account-balance?email=urwithdhanu@gmail.com`
        )
        .then((response) => {
          console.log(response.data);
          setAccountBalance(response.data);
        })
        .catch((error) => {
          if (error.response) {
            setError(
              error.response.data.error || "Error fetching account balance"
            );
          } else {
            setError("Failed to connect to the server.");
          }
        });
    } else {
      setError("User not logged in or email not found.");
    }
  }, []);

  return (
    <section className="total-balance">
      <div className="flex flex-col gap-6">
        <h2 className="header-2">
          Savings Account
          <br />
          <span className="total-balance-label">
            Account Number : {accountBalance?.accountNumber}
          </span>
        </h2>

        <div className="flex flex-col gap-2">
          <p className="total-balance-label">Total Account Balance</p>

          <div className="total-balance-amount flex-center gap-2">
            <AnimatedCounter amount={accountBalance?.balance} />
          </div>
        </div>
      </div>

      <div
        style={{ position: "absolute", right: "5%" }}
        className="total-balance-chart"
      >
        <DoughnutChart accounts={[]} />
      </div>
    </section>
  );
};

export default AccountBalance;

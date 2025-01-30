"use client";
import HeaderBox from "@/components/HeaderBox";
import RightSidebar from "@/components/RightSidebar";
import TotalBalanceBox from "@/components/TotalBalanceBox";
import RecentTransaction from "../../components/RecentTransaction";
import DialogflowWidget2 from "@/components/DialogflowWidget2";
// import { App } from "chat-app-gai";
import App from "../../components/custom-rag-chat/App";

const Home = () => {
  const loggedIn = {
    firstName: "Russel",
    lastName: "Jones",
    email: "russel@lloydsbanking.com",
  };

  return (
    <section className="home">
      <div className="home-content">
        <header className="home-header">
          <HeaderBox
            type="greeting"
            title="Welcome"
            user={loggedIn?.firstName || "Guest"}
            subtext="Access and manage your account and transactions efficiently."
          />

          <TotalBalanceBox
            accounts={[]}
            totalBanks={1}
            totalCurrentBalance={122250.35}
          />
        </header>
        RECENT TRANSACTIONS
        <RecentTransaction />
      </div>

      {/* <RightSidebar
        user={loggedIn}
        transactions={[]}
        banks={[{ currentBalance: 123.5 }, { currentBalance: 500.5 }]}
      /> */}

      {/* <DialogflowWidget2 userName={"Russel"} /> */}
      <App endpoint={"http://localhost:3000/"} />
    </section>
  );
};

export default Home;

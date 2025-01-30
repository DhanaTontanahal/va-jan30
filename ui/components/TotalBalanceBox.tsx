import AnimatedCounter from "./AnimatedCounter";
import DoughnutChart from "./DoughnutChart";
import AccountBalance from "../components/AccountBalance";
const TotalBalanceBox = ({
  accounts = [],
  totalBanks = 1,
  totalCurrentBalance,
}: TotalBalanceBoxProps) => {
  return (
    <AccountBalance />
    // <section className="total-balance">
    //   <div className="flex flex-col gap-6">
    //     <h2 className="header-2">
    //       Savings Account
    //       <br />
    //       <span className="total-balance-label">Account Number : {"1234"}</span>
    //     </h2>

    //     <div className="flex flex-col gap-2">
    //       <p className="total-balance-label">Total Account Balance</p>
    //       {/* <AccountBalance /> */}

    //       <div className="total-balance-amount flex-center gap-2">
    //         <AnimatedCounter amount={totalCurrentBalance} />
    //       </div>
    //     </div>
    //   </div>

    //   <div
    //     style={{ position: "absolute", right: "5%" }}
    //     className="total-balance-chart"
    //   >
    //     <DoughnutChart accounts={accounts} />
    //   </div>
    // </section>
  );
};

export default TotalBalanceBox;

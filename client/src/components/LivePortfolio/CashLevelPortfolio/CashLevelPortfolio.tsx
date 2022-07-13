import React, { FC, useEffect, useState } from 'react';
import styles from './CashLevelPortfolio.module.css';

import { serverAPI } from '../../../utils/serverAPI';

interface CashLevelPortfolioProps {}
interface DeskModel {
  model: string;
  pk: string;
  fields: {
    cash: number;
    updated: number;
  }
}

const CashLevelPortfolio: FC<CashLevelPortfolioProps> = () => {
  let [data, setData] = useState<DeskModel[]>([]);

  useEffect(() => {
    fetchData();
    const handleScheduledFetching = setInterval(() => {
      fetchData();
    }, 5_000);  // every 5 seconds

    return () => clearInterval(handleScheduledFetching);
  }, []);
  
  const fetchData = async () => {
    const result = await serverAPI.get('api/get_cash_portfolio');
    console.log(result.data);
    setData(result.data);
  }

  return (
  <div className={styles.CashLevelPortfolio}>
  CashLevelPortfolio Component
  <div>

  <table>
    <tbody>
      <tr>
        <th>Desk</th>
        <th>Cash</th>
      </tr>
      {data.map(item => {
        return (
          <tr key={item.pk} >
            <td>{item.pk}</td>
            <td>{Number(item.fields.cash).toFixed(2)} USX</td>
          </tr>
        )
      })}
    </tbody>
  </table>

  </div>
  </div>)
};

export default CashLevelPortfolio;

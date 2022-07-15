import React, { FC, useEffect, useState } from 'react';
import styles from './CashLevelPortfolio.module.css';

import { serverAPI } from '../../utils/serverAPI';
import { DeskModel } from '../../utils/types';
import { constants } from 'buffer';

interface CashLevelPortfolioProps { }


const CashLevelPortfolio: FC<CashLevelPortfolioProps> = () => {
  const [data, setData] = useState<DeskModel[]>([]);

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
        <b>Cash Level Portfolios</b>
        <table>
          <tbody>
            {data.map(item => {
              return (
                <td key={item.pk} >
                  <th>{item.pk}:</th>
                  <td>{Number(item.fields.cash).toFixed(2)}</td>
                </td>
              )
            })}
          </tbody>
        </table>
    </div>)
};

export default CashLevelPortfolio;

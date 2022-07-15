import React, { FC, useEffect, useState } from 'react';
import styles from './CurrencyLevelPortfolio.module.css';

import { serverAPI } from '../../../utils/serverAPI';
import { CurrencyLevelResponse } from '../../../utils/types';

interface CurrencyLevelPortfolioProps {}

const CurrencyLevelPortfolio: FC<CurrencyLevelPortfolioProps> = () => {
  const [data, setData] = useState<CurrencyLevelResponse[]>([]);

  const fetchData = async () => {
    const result = await serverAPI.get('api/get_currency_portfolio');
    console.log(result.data);
    setData(result.data);
  }

  useEffect(() => {
    fetchData();
    const handleScheduledFetching = setInterval(() => {
      fetchData();
    }, 5_000);  // every 5 seconds

    return () => clearInterval(handleScheduledFetching);
  }, []);

  return (
    <div className={styles.CurrencyLevelPortfolio}>
      <b>Currency Level Portfolios</b>
      <div>
        <table>
          <tbody>
            <tr>
              <th>Desk</th>
              <th>Currency</th>
              <th>Position</th>
              <th>NV</th>
            </tr>
            {data.map((item, index) => {
              return (
                <tr key={index} >
                  <td>{item.desk}</td>
                  <td>{item.currency}</td>
                  <td>{item.position}</td>
                  <td>{Number(item.NV).toFixed(2)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>

      </div>
    </div>
  )
};

export default CurrencyLevelPortfolio;

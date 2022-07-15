import React, { FC, useEffect, useState } from 'react';
import styles from './BondLevelPortfolio.module.css';

import { serverAPI } from '../../../utils/serverAPI';
import { BondRecordResponse } from '../../../utils/types';

interface BondLevelPortfolioProps { }

const BondLevelPortfolio: FC<BondLevelPortfolioProps> = () => {
  const [data, setData] = useState<BondRecordResponse[]>([]);

  const fetchData = async () => {
    const result = await serverAPI.get('api/get_bond_portfolio');
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
    <div className={styles.BondLevelPortfolio}>
      <b>Bond Level Portfolios</b>
      <div>
        <table>
          <tbody>
            <tr>
              <th>Desk</th>
              <th>Trader</th>
              <th>Book</th>
              <th>BondID</th>
              <th>Position</th>
              <th>NV</th>
            </tr>
            {data.map((item, index) => {
              return (
                <tr key={index} >
                  <td>{item.desk.pk}</td>
                  <td>{item.trader.pk}</td>
                  <td>{item.book.pk}</td>
                  <td>{item.bond.pk}</td>
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

export default BondLevelPortfolio;

import React, { FC, useEffect, useState } from 'react';
import styles from './Exclusions.module.css';

import { serverAPI } from '../../../utils/serverAPI';
import { ExclusionModel } from '../../../utils/types';

interface ExclusionsProps { }

const Exclusions: FC<ExclusionsProps> = () => {
  const [data, setData] = useState<ExclusionModel[]>([]);

  useEffect(() => {
    fetchData();
    const handleScheduledFetching = setInterval(() => {
      fetchData();
    }, 5_000);  // every 5 seconds

    return () => clearInterval(handleScheduledFetching);
  }, []);

  const fetchData = async () => {
    const result = await serverAPI.get('api/get_exclusion_data');
    console.log(result.data);
    setData(result.data);
  }

  return (
    <div className={styles.Exclusions}>
      <b>Exclusions</b>
      <div>
        <table>
          <tbody>
            <tr>
              <th>ID</th>
              <th>Desk</th>
              <th>Trader</th>
              <th>Book</th>
              <th>Buy/Sell</th>
              <th>Quantity</th>
              <th>BondID</th>
              <th>Price</th>
              <th>ExclusionType</th>
            </tr>
            {data.map((item, index) => {
              return (
                <tr key={index} >
                  <td>{item.pk}</td>
                  <td>{item.fields.desk}</td>
                  <td>{item.fields.trader}</td>
                  <td>{item.fields.book}</td>
                  <td>{item.fields.buy_sell}</td>
                  <td>{item.fields.quantity}</td>
                  <td>{item.fields.bond}</td>
                  <td>{item.fields.price ? Number(item.fields.price).toFixed(2) : ''}</td>
                  <td>{item.fields.exclusion_type}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
};


export default Exclusions;

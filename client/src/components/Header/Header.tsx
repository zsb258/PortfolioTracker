import React, { FC, useState, useEffect } from 'react';
import styles from './Header.module.css';

import { serverAPI } from '../../utils/serverAPI';

interface HeaderProps {}

const Header: FC<HeaderProps> = () => {
  const [data, setData] = useState<number>(-1);

  const fetchData = async () => {
    const result = await serverAPI.get('api/get_latest_event_id');
    console.log(result.data);
    setData(result.data);
  };
  fetchData();

  useEffect(() => {
    fetchData();
    const handleScheduledFetching = setInterval(() => {
      fetchData();
    }, 5_000);  // every 5 seconds

    return () => clearInterval(handleScheduledFetching);
  }, []);

  // const [waitingBar, setWaitingBar] = useState<string>('.');

  // useEffect(() => {
  //   if (waitingBar === '....'){
  //     setWaitingBar('.');
  //   }

  //   const intervalId = setInterval(() => {
  //     setWaitingBar(waitingBar + '.');
  //   }, 1000);

  //   return () => clearInterval(intervalId);

  // }, [waitingBar]);

  return (
    <div className={styles.Header}>
      Header Component
      <div>Data automatically refreshes every 5 seconds</div>
      {/* <div>{waitingBar}</div> */}
      <div>Latest event:</div>
      <div>{data}</div>
    </div>
  );
};

export default Header;

import React, { FC, useState, useEffect } from 'react';
import styles from './ReportExporter.module.css';

import { serverAPI } from '../../utils/serverAPI';

interface ReportExporterProps {}

const ReportExporter: FC<ReportExporterProps> = () => {
  const [data, setData] = useState<number>(-1);

  const fetchData = async () => {
    const result = await serverAPI.get('api/get_latest_event_id');
    console.log(result.data);
    setData(result.data);
  };
  useEffect(() => {
    fetchData();  // fetch data on component mount
  }, []);

  useEffect(() => {
    fetchData();
    const handleScheduledFetching = setInterval(() => {
      fetchData();
    }, 5_000);  // every 5 seconds

    return () => clearInterval(handleScheduledFetching);
  }, []);

  const extractTargetID = (): boolean | number => {
    const elem = document.getElementById("query_event_id") as HTMLInputElement;
    const eventID = elem ? elem.value : "1";
    const maxEventID = data;
    if (Number(eventID) <= 0 || Number(eventID) > maxEventID) {
      alert("Please input a valid event ID");
      return false;
    }
    return Number(eventID);
  }

  const onSubmit = (e: React.FormEvent<HTMLInputElement>) => {
    e.preventDefault();
    const eventID = extractTargetID();
    if (!eventID) { return; }

    window.confirm("Please wait while reports are being generated. \nPlease also allow pop-ups windows to start downloading.");
  
    const cash_url = `http://localhost:8000/api/get_cash_report?target_id=${eventID}`;
    window.open(cash_url,"_blank");
    
    const position_url = `http://localhost:8000/api/get_position_report?target_id=${eventID}`;
    window.open(position_url,"_blank");
    
    const bond_url = `http://localhost:8000/api/get_bond_report?target_id=${eventID}`;
    window.open(bond_url,"_blank");
    
    const currency_url = `http://localhost:8000/api/get_currency_report?target_id=${eventID}`;
    window.open(currency_url,"_blank");
    
    const exclusion_url = `http://localhost:8000/api/get_exclusion_report?target_id=${eventID}`;
    window.open(exclusion_url,"_blank");
  };

  async function handleGenerateReports (e: React.FormEvent<HTMLInputElement>) {
    e.preventDefault();
    const eventID = extractTargetID();
    if (!eventID) { return; }

    const result = await serverAPI.get(`api/output_reports?target_id=${eventID}`);
    window.confirm(result.data);
  }

  return (
  <div className={styles.ReportExporter}>
    <form>
      <label>Target Event ID:</label>
      <input 
        type="number" name="event_id"
        defaultValue="1" min="1" step="1" max={data.toString()}
        required
        id="query_event_id"
        />
      <label>Generate Reports</label>
      <input
        type="submit"
        onClick={handleGenerateReports} 
        value="Generate"
      />
      <label>Download Reports</label>
      <input
        type="submit"
        onClick={onSubmit} 
        value="Download"
      />
    </form>
  </div>
  )
};

export default ReportExporter;

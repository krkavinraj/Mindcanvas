import axios from "axios";

const BASE_URL = ""; 

export const getIntent = async (input) => {
  try {
    const res = await axios.post(`${BASE_URL}/api/parse-intent`, { input });
    return res.data;
  } catch (error) {
    console.error("API error:", error);
    return { widget: "unsupported", query: input };
  }
};

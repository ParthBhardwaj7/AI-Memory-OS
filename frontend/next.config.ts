import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  turbopack: {
    // Lock the compilation root directory to the frontend folder
    root: path.join(__dirname),
  },
};

export default nextConfig;

import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import copy from "rollup-plugin-copy";

export default {
  input: "src/js/main.js",
  output: {
    file: "dist/bundle.js",
    format: "iife",
    sourcemap: true,
  },
  plugins: [
    resolve(),
    commonjs(),
    copy({
      targets: [
        { src: "src/index.html", dest: "dist" },
        { src: "src/css", dest: "dist" },
        { src: "src/assets", dest: "dist" },
      ],
    }),
  ],
};



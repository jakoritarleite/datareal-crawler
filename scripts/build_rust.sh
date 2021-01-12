working_dir=${PWD}

cd ${working_dir}/src/request
cargo build --release --target-dir ${working_dir}/dist/request
cp ${working_dir}/dist/request/release/librequest.so ${working_dir}/lib/request/
cd ${working_dir}
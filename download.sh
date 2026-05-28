git clone --no-checkout https://github.com/pkity/start.git
cd start
git config core.sparseCheckout true
echo $1/ >> .git/info/sparse-checkout
git checkout master
chown -R ecs-user:ecs-user $1
cd $1/
chmod +x *.sh

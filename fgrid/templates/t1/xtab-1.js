https://stackoverflow.com/questions/70091378/error-with-remote-pagination-in-tabulator-5-0



var table = new Tabulator("#account-tran-detail-table", {
    pagination:true,
    paginationMode:"remote", //if this line is commented out then it works fine without pagination
    paginationSize: 12,
    dataSendParams:{
        page: "page",
        size: "page_size",
    },
    dataReceiveParams:{
        last_page:"total_pages",
    } ,
    ajaxResponse:function(url, params, response){
        return response.results; // return the array of table items
    },
});

table.on("tableBuilt", function(){
    table.setColumns(columns);
});

function generateReport () {
    table.clearData();
    var columns = [
            {title:"id", field:"id", headerFilter:false, visible:false, download:true},
            {title:"name", field:"name", headerFilter:false, visible:false, download:true},
        ];

    var gender = "m";
    var url = "/api/v1/myendpointname/";
    var append_params = "?gender=" + gender;

    $("#tableBuilt").destroy;
    table.setData(url + append_params);
};

--------------------------------------------------------
What format are you sending your data back in? If you are using remote pagination it needs to be slightly different from a non-paginated response. It Must be a JSONencoded object with two properties, last_page which should be an integer set to the number of the last page and data which should be set to the data array:

https://github.com/olifolkerd/tabulator/issues/1009

https://blog.katastros.com/a?ID=01700-c76b9e65-bbb4-4d6d-9715-452f495c247d



{
    "last_page":15, //the total number of available pages (this value must be greater than 0)
    "data":[ // an array of row data objects
        {id:1, name:"bob", age:"23"}, //example row data object
    ]
}
